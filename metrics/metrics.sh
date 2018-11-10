#!/bin/bash
# run using ./metrics.sh [filename{EXCLUDING FILE EXTENSION}] [poll interval] [polling iterations] [file to run] [wlan|eth] [pc|pi]
# call from directory expected by [file to run]

if [[ "$5" = "wlan" ]]; then
	sar -u $2 $3 | awk -f sar_2_csv.awk > cpu_$1.csv &
	sar -r $2 $3 | awk -f sar_2_csv.awk > mem_$1.csv &
	if [[ "$6" = "pi" ]]; then
		sar -n DEV $2 $3 | awk -f sar_net_2_csv_pi_wlan.awk > net_$1.csv &
	else
		sar -n DEV $2 $3 | awk -f sar_net_2_csv_pc_wlan.awk > net_$1.csv &
	fi
else
	sar -u $2 $3 | awk -f sar_2_csv.awk > cpu_$1.csv &
	sar -r $2 $3 | awk -f sar_2_csv.awk > mem_$1.csv &
	if [[ "$6" = "pi" ]]; then
		sar -n DEV $2 $3 | awk -f sar_net_2_csv_pi_eth.awk > net_$1.csv &
	else
		sar -n DEV $2 $3 | awk -f sar_net_2_csv_pc_eth.awk > net_$1.csv &
	fi
fi

python3 $4
