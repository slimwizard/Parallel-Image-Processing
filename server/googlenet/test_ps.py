import tensorflow as tf
import os
cwd = os.getcwd()

TESTING = False
if cwd[-len("googlenet"):] == "googlenet":
    import dist_googlenet as dg
    TESTING = True
else:
    import googlenet.dist_googlenet as dg

def pass_url_to_graph(image_url):
    cluster = tf.train.ClusterSpec({
        "worker": ["192.168.0.7:2222"],
        "ps": ["192.168.0.6:2222"]})
    return dg.build_graph(cluster, image_url)

if TESTING:
    pass_url_to_graph(None)
