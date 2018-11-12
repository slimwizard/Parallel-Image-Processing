import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# counts the number of subdirectories in a folder. recursive.
# from https://stackoverflow.com/questions/19747408/how-get-number-of-subfolders-and-folders-using-python-os-walks#19748014
def fcount(path, map = {}):
    count = 0
    for f in os.listdir(path):
        child = os.path.join(path, f)
        if os.path.isdir(child):
            child_count = fcount(child, map)
            count += child_count + 1 # unless include self
    map[path] = count
    return count


time = range(1,61)  # x axis for the plots
percentages = [0, 25, 50, 75, 100]  # left y axis
packets = [0, 10000, 20000] # right y axis


for test in ["test2", "test3", "test4", "test5"]:       # for each test 
    with open(test+"/pc/cpu_"+test+".csv", 'r') as f:           # get the pc cpu data
        reader = csv.DictReader(f)
        cpu = [line['%user'] for line in reader][:len(time)]
        cpu = np.array([float(x) for x in cpu])
    with open(test+"/pc/mem_"+test+".csv", 'r') as f:           # get the pc mem data
        reader = csv.DictReader(f)
        mem = [line['%memused'] for line in reader][:len(time)]
        mem = np.array([float(x) for x in mem])
    with open(test+"/pc/net_"+test+".csv", 'r') as f:           # get the pc net data
        reader = csv.DictReader(f)
        net = [(line['rxpck/s'],line['txpck/s']) for line in reader][:len(time)]
        net = np.array([float(rx)+float(tx) for (rx,tx) in net])

    num_pis = fcount("./"+test+"/") - 1                 # count the number of pis in this test
    fig, axes = plt.subplots(num_pis+1, 1, sharex=True) # make enough subplots

    # plot cpu and mem on the left y axis
    ax0 = axes[0]
    labels = []
    if len(cpu) == 60: labels.append(ax0.plot(time, cpu, color='b', label="%CPU Used")[0])
    if len(mem) == 60: labels.append(ax0.plot(time, mem, color='r', label="%Memory Used")[0])
    ax0.set_yticks(percentages)
    ax0.set_yticklabels([str(x) for x in percentages])

    # plot net on the right y axis
    if len(net) == 60: 
        twin = ax0.twinx()
        labels.append(twin.plot(time, net, color='y', label="Packets")[0])
        plt.yticks(packets, [str(x) for x in packets])
        
    # for each pi
    for i in range(num_pis):
        with open(test+"/pi"+str(i)+"/cpu_"+test+".csv", 'r') as f: # get the cpu data
            reader = csv.DictReader(f)
            cpu = [line['%user'] for line in reader][:len(time)]
            cpu = np.array([float(x) for x in cpu])
        with open(test+"/pi"+str(i)+"/mem_"+test+".csv", 'r') as f: # get the mem data
            reader = csv.DictReader(f)
            mem = [line['%memused'] for line in reader][:len(time)]
            mem = np.array([float(x) for x in mem])
        with open(test+"/pi"+str(i)+"/net_"+test+".csv", 'r') as f: # get the net data
            reader = csv.DictReader(f)
            net = [(line['rxpck/s'],line['txpck/s']) for line in reader][:len(time)]
            net = np.array([float(rx)+float(tx) for (rx,tx) in net])

        # plot the cpu and mem data on the left y axis
        labels = []
        if len(cpu) == 60: labels.append(axes[i+1].plot(time, cpu, color='b', label="%CPU Used")[0])
        if len(mem) == 60: labels.append(axes[i+1].plot(time, mem, color='r', label="%Memory Used")[0])
        axes[i+1].set_yticks(percentages)
        axes[i+1].set_yticklabels([str(x) for x in percentages])
        
        # plot the net data on the right y axis
        if len(net) == 60: 
            twin = axes[i+1].twinx()
            labels.append(twin.plot(time, net, color='y', label="Packets")[0])
            plt.yticks(packets, [str(x) for x in packets])
  
    # place legend
    pos = axes[0].get_position()
    axes[0].legend(labels, [p.get_label() for p in labels], loc='lower center', bbox_to_anchor=(0.5,1.1), ncol=len(labels), fancybox=True)
    axes[-1].set_xlabel("Time (s)")
    plt.savefig(test+'.png')
    plt.clf()
