#!/bin/bash

: <<'END_COMMENT'
this script checks the system's 15-minute load average and evaluates if it's high.

if the load average exceeds the number of available cpus, it may indicate system saturation.

output:
- statistic.loadavg15:<value>
- message.loadavg15:<human-readable interpretation>
END_COMMENT

# var to trigger alarm on error
statistic_error="Statistic.loadavg15:100.00"

# check /proc/cpuinfo availability
if [[ ! -r /proc/cpuinfo ]]; then
    echo "$statistic_error"
    echo "Message.loadavg1: error: /proc/cpuinfo is not accessible."
    exit 1
fi

# get load avg
load=$(uptime | awk -F 'load average: ' '{print $2}' | cut -d ',' -f 3 | xargs)

# check if load is numeric
if ! [[ "$load" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "$statistic_error"
    echo "Message.loadavg1: error: failed to read load average."
    exit 1
fi

# get cpu count
cpu_count=$(grep -c ^processor /proc/cpuinfo)

# fallback if grep fails
if [[ -z "$cpu_count" || "$cpu_count" -eq 0 ]]; then
    echo "$statistic_error"
    echo "Message.loadavg1: error: failed to determine CPU count."
    exit 1
fi

# build base message
message="Current 15-minute load average is $load on a system with $cpu_count cpu(s)."

# determine if system is overloaded
if (( $(echo "$load > $cpu_count" | bc -l) )); then
    message+=" Load average is higher than cpu count — system may be overloaded."
    top_processes=$(ps -eo pcpu,comm --sort=-pcpu| \
    awk 'NR<=5 { printf "#%d %s (CPU: %s%%); ", NR, $2, $1 }')
    message+=" Top 5 CPU-consuming processes: $top_processes"
fi

# output
echo "Statistic.loadavg15:$load"
echo "Message.loadavg15:$message"
