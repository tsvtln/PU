#!/bin/bash

: <<'END_COMMENT'
this script checks the system's 15-minute load average and evaluates if it's high.

if the load average exceeds the number of available cpus, it may indicate system saturation.

output:
- statistic.loadavg15:<value>
- message.loadavg15:<human-readable interpretation>
END_COMMENT

# get load avg and cpu count
load=$(uptime | awk -F 'load average: ' '{print $2}' | cut -d ',' -f 3 | xargs)
cpu_count=$(grep -c ^processor /proc/cpuinfo)

# build base message
message="current 15-minute load average is $load on a system with $cpu_count cpu(s)."

# determine if system is overloaded
if (( $(echo "$load > $cpu_count" | bc -l) )); then
    message+=" load average is higher than cpu count — system may be overloaded."
fi

# output
echo "Statistic.loadavg15:$load"
echo "Message.loadavg15:$message"
