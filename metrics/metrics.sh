#!/bin/bash
# run using ./metrics.sh [filename{EXCLUDING FILE EXTENSION}] [poll interval] [polling time]

sar -u $2 $3 | awk -f sar_2_csv.awk > cpu_$1.csv &
sar -r $2 $3 | awk -f sar_2_csv.awk > mem_$1.csv &

python3 example_metrics.py
