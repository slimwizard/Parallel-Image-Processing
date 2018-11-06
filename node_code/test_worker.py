import tensorflow as tf
import dist_googlenet_worker as dg
import socket

# distribute this code exactly to all workers
# functionality depends on the jobs dictionary being exactly the same
def main():
    jobs = {
            "worker": ["138.47.134.145:2222"],
            "ps": ["138.47.134.145:2223"]
           }
    cluster = tf.train.ClusterSpec(jobs)

    my_ip = get_ip()
    task = jobs["worker"].index(my_ip+':2222')

    dg.build_graph(cluster, task)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

main()
