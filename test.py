import configparser
import tensorflow as tf
from time import sleep
import multiprocessing

config = configparser.ConfigParser()
config.read("./ps_worker.ini")
jobs = { "worker" : config["IP Listing"]["worker"].split(", ")
         "ps" : config["IP Listing"]["ps"]
}
cluster = tf.train.ClusterSpec(jobs)

def ps():
    # create shared variable on ps task
    with tf.device("/job:ps/task:0"):
        var = tf.Variable(0.0, name='var')

    server = tf.train.Server(cluster, job_name="ps", task_index=0)
    sess = tf.Session(target=server.target)

    print("waiting on cluster connection")

    # should not do this until the whole cluster is ready
    sess.run(tf.global_variables_initializer())
    print("variables initialized")

    val = 0.0
    while val < 5.0:
        val = sess.run(var)
        print("var has value %.1f" %val)
        sleep(1.0)

def worker(N):
    # create shared variable on ps task
    with tf.device("/job:ps/task:0"):
        var = tf.Variable(0.0, name='var')

    server = tf.train.Server(cluster, job_name="worker", task_index=N)
    sess = tf.Session(target=server.target)

    print("waiting on cluster connection")

    # should not do this until the whole cluster is ready
    while sess.run(tf.report_uninitialized_variables()):
        print("waiting on variable initialization")
        sleep(1.0)

    for i in range(5):
        print("adding 1 to var")
        sess.run(var.assign_add(1.0))
        sleep(1.0)

ps()
