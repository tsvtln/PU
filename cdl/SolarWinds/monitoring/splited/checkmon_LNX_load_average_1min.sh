#!/bin/bash

: <<'END_COMMENT'
this script checks the system's 1-minute load average and evaluates if it's high.

if the load average exceeds the number of available cpus, it may indicate system saturation.

output:
- statistic.loadavg1:<value>
- message.loadavg1:<human-readable interpretation>
END_COMMENT

# get load avg and cpu count
load=$(uptime | awk -F 'load average: ' '{print $2}' | cut -d ',' -f 1 | xargs)
cpu_count=$(grep -c ^processor /proc/cpuinfo)

# build base message
message="current 1-minute load average is $load on a system with $cpu_count cpu(s)."

# determine if system is overloaded
if (( $(echo "$load > $cpu_count" | bc -l) )); then
    message+=" load average is higher than cpu count — system may be overloaded."
fi

# output
echo "Statistic.loadavg1:$load"
echo "Message.loadavg1:$message"
