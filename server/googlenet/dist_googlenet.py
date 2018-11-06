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
    # probabilities listing
    prob_list = return_list
    # default picture for testing
    if image_url == None:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Bow_bow.jpg/800px-Bow_bow.jpg"

    server = tf.train.Server(cluster, job_name="ps", task_index=0)

    #download the inception v1 checkpoint
    url = "http://download.tensorflow.org/models/inception_v1_2016_08_28.tar.gz"
    checkpoints_dir = '/tmp/checkpoints'

    if not tf.gfile.Exists(checkpoints_dir):
        tf.gfile.MakeDirs(checkpoints_dir)

    if not tf.gfile.Exists(checkpoints_dir+'/inception_v1_2016_08_28.tar.gz'):
        dataset_utils.download_and_uncompress_tarball(url, checkpoints_dir)
    # end download



    image_size = inception.inception_v1_dist.default_image_size
    with tf.Graph().as_default():
        # create a "done queue" to be filled by other servers when they're
            # through with computation that this server depends on
        # here, each worker task must enqueue something
        with tf.device('/job:ps/task:0'):
            done_queue = tf.FIFOQueue(cluster.num_tasks('worker'), tf.int32, shared_name='done_queue')
            img_ready_queue = tf.FIFOQueue(cluster.num_tasks('worker'), tf.int32, shared_name='done_queue')

            # image preprocessing
            image_string = urllib.urlopen(image_url).read()
            image = tf.image.decode_jpeg(image_string, channels=3)
            processed_image = inception_preprocessing.preprocess_image(image, image_size, image_size, is_training=False)
            processed_images  = tf.expand_dims(processed_image, 0)
            shared_image = tf.identity(processed_images, name="shared_image")
            
            #TODO: call enqueue_many to put one item on queue per worker
                # do this after stopping is fixed
            enqueue_op = img_ready_queue.enqueue
            
        # tell the workers the image preprocessing is done
        run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
        run_metadata = tf.RunMetadata()
        tf.Session(server.target).run(enqueue_op(1), options=run_options, run_metadata=run_metadata)
        #print("Image ready enqueue!")

        # Create the model, use the default arg scope to configure the batch norm parameters.
        with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
            with tf.device(tf.train.replica_device_setter(cluster=cluster)):
                logits, _ = inception.inception_v1_dist(shared_image, num_classes=1001, is_training=False)
                probabilities = tf.nn.softmax(logits)

        # initialization function that uses saved parameters
        init_fn = slim.assign_from_checkpoint_fn(
            os.path.join(checkpoints_dir, 'inception_v1.ckpt'),
            slim.get_model_variables('InceptionV1'))


        # time for logging
        now = str(datetime.now())
        now = now[:now.find('.')]
        logdir = './logs/'+now
        if not tf.gfile.Exists(logdir):
            tf.gfile.MakeDirs(logdir)

        with tf.Session(target=server.target) as sess:
            # recording metadata
            run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
            run_metadata = tf.RunMetadata()
            file_writer = tf.summary.FileWriter('./logs/'+now, sess.graph)

            # run the thing
            init_fn(sess)
            np_image, probabilities = sess.run([image, probabilities], options=run_options, run_metadata=run_metadata)

            # see who did what
            for device in run_metadata.step_stats.dev_stats:
                print(device.device)
                for node in device.node_stats:
                    print("  ", node.node_name)

            # instead of join(), wait until all workers have put their 'done' token on the queue
            # now printing for debugging
            for i in range(cluster.num_tasks('worker')):
                run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
                run_metadata = tf.RunMetadata()
                sess.run(done_queue.dequeue(), options=run_options, run_metadata=run_metadata)
                #print("Done dequeue!")

            # log metadata
            file_writer.add_run_metadata(run_metadata, now)
            file_writer.close()

            probabilities = probabilities[0, 0:]
            sorted_inds = [i[0] for i in sorted(enumerate(-probabilities), key=lambda x:x[1])]


        # display results
        plt.figure()
        plt.imshow(np_image.astype(np.uint8))
        plt.axis('off')
        plt.show()

        names = imagenet.create_readable_names_for_imagenet_labels()
        for i in range(5):
            index = sorted_inds[i]
            probability = 'Probability %0.2f%% => [%s]' % (probabilities[index] * 100, names[index])
            prob_list.append(probability)
            print(probability)
