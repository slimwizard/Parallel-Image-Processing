import argparse
import paramiko
import re
import subprocess

# compiles regex string that matches IPv4 addresses
def is_ip_addr(test_string):
    ip_addr_string = re.compile("(?:[0-9]{1,3}\.){3}[0-9]{1,3}")
    is_ip_addr = ip_addr_string.match(test_string)
    return is_ip_addr

# checks if it is a pi with a default login
def is_default_pi(ip_addr):
    return True

#TODO(CP) get current IP for ps

# parse args
parser = argparse.ArgumentParser()
parser.add_argument("ip")
args = parser.parse_args()

# if it's an IP given, run the nmap to find all open ssh connections
if is_ip_addr(args.ip):
    find_pi = "nmap -T5 " + args.ip + "/24 -p 22"
    find_pi = find_pi + "| grep -B4 open | grep -Po '(?:[0-9]{1,3}\.){3}[0-9]{1,3}'"
else:
    raise ValueError("Please input a valid IP address.")

# run the command and make a list of its output
ip_addr_list = subprocess.Popen(find_pi, shell=True, stdout=subprocess.PIPE)
ip_stdout, ip_stderr = ip_addr_list.communicate()
ip_addr_list = ip_stdout.decode("utf-8")
ip_addr_list = ip_addr_list.split("\n")

# remove any false positives
ip_addr_clone_list = ip_addr_list
for ip_addr in ip_addr_clone_list:
    if is_ip_addr(ip_addr):
        continue
    else:
        ip_addr_list.remove(ip_addr)



print(str(ip_addr_list))
