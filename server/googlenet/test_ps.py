import tensorflow as tf
import dist_googlenet as dg

def pass_url_to_graph(image_url):
    cluster = tf.train.ClusterSpec({
        "worker": ["192.168.0.7:2222"],
        "ps": ["192.168.0.4:2222"]})

    image_url = 'https://upload.wikimedia.org/wikipedia/commons/7/70/EnglishCockerSpaniel_simon.jpg'
    dg.build_graph(cluster, image_url)
