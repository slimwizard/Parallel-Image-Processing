#!/bin/bash
# run using ./metrics.sh [filename{EXCLUDING FILE EXTENSION}] [polling time]

sar -u 1 $2 | awk -f sar_2_csv.awk > cpu_$1.csv &
sar -r 1 $2 | awk -f sar_2_csv.awk > mem_$1.csv &

python3 example_metrics.py
