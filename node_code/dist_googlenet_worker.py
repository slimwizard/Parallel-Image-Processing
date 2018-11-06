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
sys.path.append("./models/research/slim/")

from datasets import imagenet
from datasets import dataset_utils
from nets import inception
from preprocessing import inception_preprocessing

from tensorflow.contrib import slim

def build_graph(cluster, task):
    server = tf.train.Server(cluster, job_name='worker', task_index=task)

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
        # create a queues to be shared with the ps
        with tf.device('/job:worker/task:'+str(task)):
            done_queue = tf.FIFOQueue(cluster.num_tasks('worker'), tf.int32, shared_name='done_queue', shapes=[])
            img_ready_queue = tf.FIFOQueue(cluster.num_tasks('worker'), tf.int32, shared_name='img_ready_queue')
       
            # use this queue to block until shared_image is ready
            dequeue_op = img_ready_queue.dequeue()
       
            print("before img dequeue op")
            tf.Session(server.target).run(dequeue_op)
            print("Image ready dequeue!")
            
            # now get the image
            shared_image_shape = np.array([1, 224, 224, 3])  # not great to hard code, but eh
            shared_image = tf.get_variable("shared_image", shared_image_shape, tf.float32)

        # Create the model, use the default arg scope to configure the batch norm parameters.
        with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
            with tf.device(tf.train.replica_setter(cluster=cluster)):
                logits, _ = inception.inception_v1_dist(shared_image, num_classes=1001, is_training=False)
                probabilities = tf.nn.softmax(logits)
        
        init_fn = slim.assign_from_checkpoint_fn(
            os.path.join(checkpoints_dir, 'inception_v1.ckpt'),
            slim.get_model_variables('InceptionV1'))
        

        with tf.Session(target=server.target) as sess:
            init_fn(sess)
            probabilities = sess.run(probabilities)
            
            # instead of server.join(), add to the queue
            print("before done enqueue")
            sess.run(done_queue.enqueue(1))
            print("after done enqueue")
            #print("Done enqueue!")
