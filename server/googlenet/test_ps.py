import tensorflow as tf
import configparser
import os
cwd = os.getcwd()

TESTING = False

if cwd[-len("googlenet"):] == "googlenet": # for calling this file as the entry point, from this directory
    import dist_googlenet as dg
    ini_path = "../../node_code/ps_worker.ini"
    TESTING = True
else:
    import googlenet.dist_googlenet as dg # for calling server.py as the entry point, from the server directory
    ini_path = "../node_code/ps_worker.ini"

def pass_url_to_graph(image_url, return_list):
    config = configparser.ConfigParser()
    config.read(ini_path)
    workers_listing = []
    ps_listing = []

    for worker in config["IP Listing"]["worker"].split(", "):
        worker = str(worker) + ":2222"
        workers_listing.append(worker)

    for ps in [config["IP Listing"]["ps"]]:
        ps = str(ps) + ":2222"
        ps_listing.append(ps)

    jobs = { "worker" : workers_listing,
             "ps" : ps_listing
    }
    cluster = tf.train.ClusterSpec(jobs)
    
    dg.build_graph(cluster, image_url, return_list)

if TESTING:
    pass_url_to_graph(None, [])
