from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os
import tensorflow as tf
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

import os
import sys
cwd = os.getcwd()
if cwd[-len("googlenet"):] == "googlenet": # if we're testing and running direclty from the googlenet/ folder
    sys.path.append("../../models/research/slim/")
else:
    sys.path.append("../models/research/slim/")

from datasets import imagenet
from datasets import dataset_utils
from nets import inception
from preprocessing import inception_preprocessing

from tensorflow.contrib import slim

def build_graph(cluster, image_url, return_list):
    # shared list on the ps task indicating which tasks have completed
    with tf.device("/job:ps/task:0"):
        done_list = tf.get_variable("done_list", [cluster.num_tasks('worker')+1], tf.int32, tf.zeros_initializer)

    # probabilities listing
    prob_list = return_list
    
    # default picture for testing
    if image_url == None:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Bow_bow.jpg/800px-Bow_bow.jpg"

    #download the inception v1 checkpoint if we need to 
    url = "http://download.tensorflow.org/models/inception_v1_2016_08_28.tar.gz"
    checkpoints_dir = '/tmp/checkpoints'
    if not tf.gfile.Exists(checkpoints_dir):
        tf.gfile.MakeDirs(checkpoints_dir)
    if not tf.gfile.Exists(checkpoints_dir+'/inception_v1_2016_08_28.tar.gz'):
        dataset_utils.download_and_uncompress_tarball(url, checkpoints_dir)
    # end download

    server = tf.train.Server(cluster, job_name="ps", task_index=0)
    sess = tf.Session(target=server.target)

    # image preprocessing
    image_size = inception.inception_v1_dist.default_image_size
    image_string = urllib.urlopen(image_url).read()
    image = tf.image.decode_jpeg(image_string, channels=3)
    processed_image = inception_preprocessing.preprocess_image(image, image_size, image_size, is_training=False)
    processed_images  = tf.expand_dims(processed_image, 0)
    shared_image = tf.identity(processed_images, name="shared_image")   
            
    # tell the workers the image preprocessing is done
    with tf.device("/job:ps/task:0"):
        img_done = tf.Variable(0, name='img_done')
    sess.run(tf.global_variables_initializer())
    sess.run(img_done.assign_add(1))

    # Create the model, use the default arg scope to configure the batch norm parameters.
    with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
        with tf.device(tf.train.replica_device_setter(cluster=cluster)):
            logits, _ = inception.inception_v1_dist(shared_image, num_classes=1001, is_training=False)
            probabilities = tf.nn.softmax(logits)

    # initialization function that uses saved parameters
    init_fn = slim.assign_from_checkpoint_fn(
        os.path.join(checkpoints_dir, 'inception_v1.ckpt'),
        slim.get_model_variables('InceptionV1'))
    init_fn(sess)
    
    # do the thing
    print("before getting probs")
    np_image, probabilities = sess.run([image, probabilities], options=run_options, run_metadata=run_metadata)
    print("after getting probs")

    # indicate that the ps task is done
    tf.scatter_update(done_list, [0], 1)
   
    # wait until all tasks are done
    while sess.run(tf.reduce_sum(done_list)) < cluster.num_tasks('worker')+1:
        pass

    sess.close()

    # see who did what
    for device in run_metadata.step_stats.dev_stats:
        print(device.device)
        for node in device.node_stats:
            print("  ", node.node_name)

    probabilities = probabilities[0, 0:]
    sorted_inds = [i[0] for i in sorted(enumerate(-probabilities), key=lambda x:x[1])]


    # display results
    #plt.figure()
    #plt.imshow(np_image.astype(np.uint8))
    #plt.axis('off')
    #plt.show()

    names = imagenet.create_readable_names_for_imagenet_labels()
    for i in range(5):
        index = sorted_inds[i]
        probability = 'Probability %0.2f%% => [%s]' % (probabilities[index] * 100, names[index])
        prob_list.append(probability)
        print(probability)
