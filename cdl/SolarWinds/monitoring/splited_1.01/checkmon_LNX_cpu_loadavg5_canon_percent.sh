#!/bin/bash

: <<'END_COMMENT'
gets the system activity information from the last 5min through sar and reports back
usually sar should come ootb, but there are checks if it's missing for w/e reason

This metric is a representing the system load average for the 5 minutes.  The load average is calculated as
the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible
sleep (D state) over the specified interval.It has to be analyzed compared of the current number
of cpu cpu_nb
END_COMMENT

# unused (kept here for reference)
#WARN_def=125
#CRIT_def=150

# stat to trigger alarm
error_statistic="Statistic:100"


# check if sar exists
if ! command -v sar >/dev/null; then
  echo "$error_statistic"
  echo "Message: Unable to find 'sar' command - check if it's installed."
  exit 1
fi

# get the count of cpus
cpu_nb=$(grep -c processor /proc/cpuinfo)

# grep the location of the sar file
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
cpu_loadavg5=$(echo "$sar_cpu_avg_load" | awk '/^Average:/{print $5}' | cut -d'.' -f1 )
cpu_loadavg5_cannon_percent=$((100 * cpu_loadavg5 / cpu_nb))

# preset outs
stats_out="Statistic.cpu_loadavg5_cannon_percent:$cpu_loadavg5_cannon_percent"
msg_out="Message.cpu_loadavg5_cannon_percent: CPU canon average load last 1minute: $cpu_loadavg5_cannon_percent.
 CPU average load: $cpu_loadavg5. Number of cores on this node is $cpu_nb."

# check if high % to append top processes
if [ $cpu_loadavg5_cannon_percent -ge 90 ]; then
  top_processes=$(ps -eo pcpu,comm --sort=-pcpu | \
  awk 'NR<=5 { printf "#%d %s (CPU: %s%%); ", NR, $2, $1 }')
  msg_out+=" Top 5 CPU-consuming processes: $top_processes"
fi

# print outputs
echo "$stats_out"
echo "$msg_out"|tr -d '\n'|paste -sd ''
