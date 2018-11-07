#!/bin/bash
# run using ./metrics.sh [filename{EXCLUDING FILE EXTENSION}] [poll interval] [polling iterations] [file to run]

sar -u $2 $3 | awk -f sar_2_csv.awk > cpu_$1.csv &
sar -r $2 $3 | awk -f sar_2_csv.awk > mem_$1.csv &
sar -n DEV $2 $3 | awk -f sar_net_2_csv.awk > net_$1.csv &

python3 $4
