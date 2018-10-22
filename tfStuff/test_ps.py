'''
Minimal working example of distributed tensorflow.
Run this script on both machines with appropriate addresses.
On one machine, change the job_name argument within Server() to "worker"
'''

import tensorflow as tf

cluster = tf.train.ClusterSpec({
    "worker": ["192.168.0.7:2222"],
    "ps": ["192.168.0.4:2222"]
    })

server = tf.train.Server(cluster, job_name="ps", task_index=0)

# by requiring the workers to have the token to continue, we
	# force them to wait for the ps job to initiate computation
with tf.device("/job:ps/task:0"):
    token = tf.constant(1, tf.float32)
    x = tf.get_variable("w1", [2,2], tf.float32, tf.zeros_initializer())
    y = tf.get_variable("w2", [2,2], tf.float32, tf.zeros_initializer())    


with tf.device("/job:worker/task:0"):
    x = tf.scalar_mul(token, x)
    y = tf.scalar_mul(token, y)
    x = x + 2
    y = y + 3
    x = tf.Print(x, [x], "WORKER PRINT")

with tf.device("job:ps/task:0"):
    y = tf.Print(y, [y], "PS PRINT")
    sum_ = x + y

init = tf.global_variables_initializer()
with tf.Session(server.target) as sess:
    sess.run(init)
    print(sess.run(sum_))
