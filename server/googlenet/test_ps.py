import tensorflow as tf
import os
cwd = os.getcwd()

TESTING = False
if cwd[-len("googlenet"):] == "googlenet":
    import dist_googlenet as dg
    TESTING = True
else:
    import googlenet.dist_googlenet as dg

def pass_url_to_graph(image_url, return_list):
    cluster = tf.train.ClusterSpec({
        "worker": ["138.47.134.145:2222"],
        "ps": ["138.47.134.145:2223"]})
    dg.build_graph(cluster, image_url, return_list)

if TESTING:
    pass_url_to_graph(None, [])
