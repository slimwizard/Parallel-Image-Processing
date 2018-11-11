import argparse
import configparser
import netifaces
import paramiko
import re
import subprocess
from os.path import expanduser

# compiles regex string that matches IPv4 addresses
def is_ip_addr(test_string):
    ip_addr_string = re.compile("(?:[0-9]{1,3}\.){3}[0-9]{1,3}")
    is_ip_addr = ip_addr_string.match(test_string)
    return is_ip_addr

# checks if it is a pi with a default login
def is_default_pi(ip_addr, trust_unknown_hosts=False):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()

    # if you want, trust unknown hosts
    if trust_unknown_hosts:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip_addr, username="pi", password="raspberry")
    except paramiko.ssh_exception.AuthenticationException as error:
        print("Cannot connect to {0}, the following error "
              "occured: {1}".format(ip_addr, str(error)))
        return False
    except paramiko.ssh_exception.SSHException as error:
        print("Cannot connect to {0}, the following error "
              "occured: {1}".format(ip_addr, str(error)))
        return False
    ssh.close()
    return True

# remove anything in a list that isn't a pi's IP address
def remove_non_pi(ip_addr_list, trust_unknown_hosts=False):
    print("The IP addresses that will be checked if they are "
          "Raspberry Pi's: {0}".format(ip_addr_list))

    # remove any false positives that aren't IP's
    ip_addr_clone_list = ip_addr_list
    for ip_addr in ip_addr_clone_list:
        if is_ip_addr(ip_addr):
            continue
        else:
            ip_addr_list.remove(ip_addr)

    # remove any IP's that aren't default configured pi's
    ip_addr_clone_list = ip_addr_list
    for ip_addr in ip_addr_clone_list:
        if is_default_pi(ip_addr, trust_unknown_hosts):
            continue
        else:
            ip_addr_list.remove(ip_addr)
    print("The IP addresses that are default configured "
          "Raspberry Pi's: {0}".format(ip_addr_list))
    return ip_addr_list

# if an error is found here, check what interfaces are running and adjust
def get_curr_ip():
    return netifaces.ifaddresses("eno1")[netifaces.AF_INET][0]["addr"]

def discover(ip): 
    # if it's an IP given, run the nmap to find all open ssh connections
    if is_ip_addr(ip):
        find_pi = "nmap -T4 " + ip + "/24 -p 22"
        find_pi = find_pi + "| grep -B4 open | grep -Po '(?:[0-9]{1,3}\.){3}[0-9]{1,3}'"
    else:
        raise ValueError("Please input a valid IP address.")

    # run the command and make a list of its output
    ip_addr_list = subprocess.Popen(find_pi, shell=True, stdout=subprocess.PIPE)
    ip_stdout, ip_stderr = ip_addr_list.communicate()
    ip_addr_list = ip_stdout.decode("utf-8")
    ip_addr_list = ip_addr_list.split("\n")
    ip_addr_list = remove_non_pi(ip_addr_list)
    curr_ip = get_curr_ip()

    # create config file
    config = configparser.ConfigParser()
    config["IP Listing"] = {"worker" : ", ".join(ip_addr_list),
                            "ps" : curr_ip}
    config_file = expanduser("~/cloud_computing/Parallel-Image-Processing/node_code/ps_worker.ini")
    with open(config_file, "w") as configfile:
        config.write(configfile)
