import tensorflow as tf
def TestGraph():
    with tf.device("/job:ps/task:0"):
        a = tf.get_variable("a",[1,2],tf.float32,tf.zeros_initializer())
        a = a + 2
        a = tf.Print(a, [a], "PS PRINT")

    with tf.device("/job:worker/task:0"):
        a = a + 3
        a = tf.Print(a, [a], "WORKER PRINT")

    return a
