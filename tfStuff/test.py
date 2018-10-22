'''
Minimal working example of distributed tensorflow.
Run this script on both machines with appropriate addresses.
On one machine, change the job_name argument within Server() to "worker"
Prints twice because both machines will be calling sess.run(sum_)
'''

import tensorflow as tf

cluster = tf.train.ClusterSpec({
    "worker": ["192.168.0.7:2222"],
    "ps": ["192.168.0.4:2222"]
    })

server = tf.train.Server(cluster, job_name="ps", task_index=0)

with tf.device("/job:worker/task:0"):
    weights_1 = tf.get_variable("w1", [2,2], tf.float32, tf.zeros_initializer())
    weights_1 = weights_1 + 2
    weights_1 = tf.Print(weights_1, [weights_1], "WORKER JOB PRINT")

with tf.device("/job:ps/task:0"):
    weights_2 = tf.get_variable("w2", [2,2], tf.float32, tf.zeros_initializer())    
    weights_2 = weights_2 + 3
    weights_2 = tf.Print(weights_2, [weights_2], "PS JOB PRINT")
    sum_ = weights_1 + weights_2

init = tf.global_variables_initializer()
with tf.Session(server.target) as sess: # Create a session on the server.
    sess.run(init)
    print(sess.run(sum_))
