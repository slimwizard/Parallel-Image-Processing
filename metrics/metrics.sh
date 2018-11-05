#!/bin/bash
# run using ./metrics.sh [filename] [time to collect]

sar -u 1 $2 | awk -f sar_2_csv.awk > $1 &

python3 example_metrics.py
