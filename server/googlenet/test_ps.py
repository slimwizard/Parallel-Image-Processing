import tensorflow as tf
import os
cwd = os.getcwd()

TESTING = False

if cwd[-len("googlenet"):] == "googlenet": # for calling this file as the entry point, from this directory
    import dist_googlenet as dg
    TESTING = True
else:
    import googlenet.dist_googlenet as dg # for calling server.py as the entry point, from the server directory

def pass_url_to_graph(image_url, return_list):
    cluster = tf.train.ClusterSpec({
            "worker": [ "192.168.0.2:2222"#,
                        #"192.168.86.176:2222",
                        #"192.168.86.172:2222"
                      ],
            "ps": ["192.168.0.6:2222"]
    dg.build_graph(cluster, image_url, return_list)

if TESTING:
    pass_url_to_graph(None, [])
