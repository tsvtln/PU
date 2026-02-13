#!/bin/bash

: <<'END_COMMENT'
gets the system activity information from the last 15min through sar and reports back
usually sar should come ootb, but there are checks if it's missing for w/e reason

This metric is a representing the system canonical per-cpu based load average for the 15 minutes.
The load average is calculated as the average number of runnable or running tasks (R state),
and the number of tasks in uninterruptible sleep (D state) over the specified interval.
The result is devised by the current number of cpu cpu_nb=$cpu_nb and given in percentage"
END_COMMENT

# unused vars
# MAX_SAR_COUNT=5
# DEBUG=0
#WARN_def=125
#CRIT_def=150

# stat to trigger alarm
error_statistic="Statistic:100"

# checking if sar exists
if ! command -v sar >/dev/null; then
    echo "$error_statistic"
    echo "Message: Unable to find 'sar' command -
 please check and install it on the target server."  |tr -d '\n'|paste -sd ''
    exit 1
fi

# gathering count of cpus
cpu_nb=$(grep -c processor /proc/cpuinfo)

# grepping the sar file location
SARFILE=""

# location used in RHEL and SLES
if [[ -f /var/log/sa/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sa/sa$(date '+%d')

# location used in Ubuntu (and debian if needed)
elif [[ -f /var/log/sysstat/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sysstat/sa$(date '+%d')
else
    echo "$error_statistic"
    echo "Message.cpu_loadavg5_cannon_percent: ERROR: 'sar' command not found.
 Please install and configure sysstat. Make sure services are enabled afterwards."|tr -d '\n'|paste -sd ''
    exit 1
fi

# writing into vars the avg load
sar_cpu_avg_load=$(sar -q -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/ { print $0 }')
cpu_loadavg15=$(echo "$sar_cpu_avg_load" | awk '{print $6}' | cut -d'.' -f1)
cpu_loadavg15_cannon_percent=$((100 * cpu_loadavg15 / cpu_nb))

# preset outs
stats_out="Statistic.cpu_loadavg15_cannon_percent:$cpu_loadavg15_cannon_percent"
msg_out="Message.cpu_loadavg15_cannon_percent: CPU canon average load last 1minute: $cpu_loadavg15_cannon_percent.
 CPU average load: $cpu_loadavg15. Number of cores on this node is $cpu_nb."

# check if high % to append top processes
if [ $cpu_loadavg15_cannon_percent -ge 90 ]; then
  top_processes=$(ps -eo pcpu,comm --sort=-pcpu | \
  awk 'NR<=5 { printf "#%d %s (CPU: %s%%); ", NR, $2, $1 }')
  msg_out+=" Top 5 CPU-consuming processes: $top_processes"
fi

# print outputs
echo "$stats_out"
echo "$msg_out"|tr -d '\n'|paste -sd ''
