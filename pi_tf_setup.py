import configparser
import os
import paramiko

config_file = "./node_code/ps_worker.ini"
local_node_code = "./node_code/"
local_node_code_files = os.listdir("./node_code")
print(local_node_code_files)
remote_node_code = "/home/pi/cloud_computing/Parallel-Image-Processing/node_code"
config = configparser.ConfigParser()
config.read(config_file)
jobs = dict(config.items("IP Listing"))

print(jobs["worker"])
for host in jobs["worker"].split(", "):
    print("Placing the ps_worker.ini file on {0}.".format(host))
    transport = paramiko.Transport((host, 22))
    transport.connect(username="pi", password="raspberry")
    sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)
    for node_file in local_node_code_files:
        sftp.put(node_file, remote_node_code, confirm=True)
