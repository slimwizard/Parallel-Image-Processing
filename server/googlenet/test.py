import tensorflow as tf

fq = tf.FIFOQueue(4, tf.int32, shapes=[[]])
op1 = fq.enqueue_many(tf.fill([4], 1))
x = 4
op2 = fq.dequeue_many(x)

with tf.Session() as sess:
    sess.run(op1)
    sess.run(op2)
