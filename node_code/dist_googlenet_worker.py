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
    # shared list on the ps task indicating which tasks have completed
    with tf.device("/job:ps/task:0"):
        done_list = tf.get_variable("done_list", [cluster.num_tasks('worker')+1], tf.int32, tf.zeros_initializer)
    
    server = tf.train.Server(cluster, job_name='worker', task_index=task)
    sess = tf.Session(target=server.target)

    # shared image 
    image_size = inception.inception_v1_dist.default_image_size
    shared_image_shape = np.array([1, image_size, image_size, 3])
    shared_image = tf.get_variable("shared_image", shared_image_shape, tf.float32)

    # build the graph
    with slim.arg_scope(inception.inception_v1_dist_arg_scope()):
        with tf.device(tf.train.replica_setter(cluster=cluster)):
            logits, _ = inception.inception_v1_dist(shared_image, num_classes=1001, is_training=False)
            probabilities = tf.nn.softmax(logits)
        
    # wait until all variables are initialized
    while sess.run(tf.report_uninitialized_variables()):
        pass
    
    # wait until ps task is done
    while sess.run(tf.reduce_sum(done_list)) == 0:
        pass
        
    # this task must be done?
    tf.scatter_update(done_list, [task+1], 1)
  
    sess.close()
