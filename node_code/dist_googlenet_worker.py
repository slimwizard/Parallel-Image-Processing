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

def build_graph(cluster, task):
    image_size = inception.inception_v1_dist.default_image_size
    shared_image_shape = np.array([1, image_size, image_size, 3])
    
    # shared done list and shared image 
    with tf.device("/job:ps/task:0"):
        done_list = tf.get_variable("done_list", [cluster.num_tasks('worker')+1], tf.int32, tf.zeros_initializer)
        shared_image = tf.get_variable("shared_image", shared_image_shape, tf.float32)
    
    server = tf.train.Server(cluster, job_name='worker', task_index=task)
    sess = tf.Session(target=server.target)

    # build the graph
    with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
        with tf.device(tf.train.replica_device_setter(cluster=cluster)):
            logits, _ = inception.inception_v1_dist(shared_image, num_classes=1001, is_training=False)
            probabilities = tf.nn.softmax(logits)
        
    # wait until all variables are initialized
    print("waiting for variables to be initialized")
    uninit = sess.run(tf.report_uninitialized_variables())
    while len(uninit) > 0:
        print(uninit)
        uninit = sess.run(tf.report_uninitialized_variables())
    
    # wait until ps task is donei
    print("waiting for ps to be done")
    while sess.run(tf.reduce_sum(done_list)) == 0:
        pass
        
    # this task must be done?
    print("I am done")
    sess.run(tf.scatter_update(done_list, [task+1], 1))
  
    sess.close()
