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

import sys
sys.path.append("../models/research/slim/")

from datasets import imagenet
from datasets import dataset_utils
from nets import inception
from preprocessing import inception_preprocessing

from tensorflow.contrib import slim

def build_graph(cluster):
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
            queue = tf.FIFOQueue(cluster.num_tasks('worker'), tf.int32, shared_name='done_queue')
        
        
        url = 'https://upload.wikimedia.org/wikipedia/commons/7/70/EnglishCockerSpaniel_simon.jpg'
        image_string = urllib.urlopen(url).read()
        image = tf.image.decode_jpeg(image_string, channels=3)
        processed_image = inception_preprocessing.preprocess_image(image, image_size, image_size, is_training=False)
        processed_images  = tf.expand_dims(processed_image, 0)
        
        # Create the model, use the default arg scope to configure the batch norm parameters.
        with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
            logits, _ = inception.inception_v1_dist(processed_images, num_classes=1001, is_training=False)
        probabilities = tf.nn.softmax(logits)
        
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

            # maybe I need this?
            tf.summary.scalar('dummy', tf.reduce_mean(probabilities))
            merged = tf.summary.merge_all()

            # run the thing
            init_fn(sess)
            summary, np_image, probabilities = sess.run([merged, image, probabilities], options=run_options, run_metadata=run_metadata)
            
            # instead of join(), wait until all workers have put their 'done' token on the queue
            for i in range(cluster.num_tasks('worker')):
                sess.run(queue.dequeue())
            
            # log metadata
            file_writer.add_run_metadata(run_metadata, now)
            file_writer.add_summary(summary, 1)
            file_writer.close()

            probabilities = probabilities[0, 0:]
            sorted_inds = [i[0] for i in sorted(enumerate(-probabilities), key=lambda x:x[1])]


        # display results
        print("starting plotting")
        plt.figure()
        plt.imshow(np_image.astype(np.uint8))
        plt.axis('off')
        plt.show()

        names = imagenet.create_readable_names_for_imagenet_labels()
        for i in range(5):
            index = sorted_inds[i]
            print('Probability %0.2f%% => [%s]' % (probabilities[index] * 100, names[index]))
