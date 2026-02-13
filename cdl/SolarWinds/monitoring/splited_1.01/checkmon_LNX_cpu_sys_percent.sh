#!/bin/bash

: <<'END_COMMENT'
read sar -f ... for CPU usage (not -q this time, but regular sar)
extract column 5 (system time %)
output the stat and message, using the right thresholds

This metric refers to the percentage of time the CPU spent executing system
(kernel) code. High values can indicate heavy I/O, syscall, or context switches.
END_COMMENT

# stat to trigger alarm
error_statistic="Statistic.cpu_sys_percent:100"

# checking if sar exists
if ! command -v sar >/dev/null; then
    echo "$error_statistic"
    echo "Message.cpu_sys_percent: Unable to find 'sar' command - please check and install it on the
 target server." | tr -d '\n' | paste -sd ''
    exit 1
fi

# grepping the sar file location
SARFILE=""
if [[ -f /var/log/sa/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sa/sa$(date '+%d')
elif [[ -f /var/log/sysstat/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sysstat/sa$(date '+%d')
else
    echo "$error_statistic"
    echo "Message.cpu_sys_percent: ERROR: 'sar' command not found.
 Please install and configure sysstat. Make sure services are enabled afterwards."|tr -d '\n'|paste -sd ''
    exit 1
fi

# get system CPU %
sar_cpu_avg_line=$(sar -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
cpu_sys_percent=$(echo "$sar_cpu_avg_line" | awk '{print $5}' | cut -d'.' -f1)

# default message
message="Current CPU usage by the system: $cpu_sys_percent%.
 High values can indicate heavy I/O, syscall, or context switches."

# if over threshold, include top 5 processes
if [[ $cpu_sys_percent -ge 90 ]]; then
    top_processes=$(ps -eo pcpu,comm --sort=-pcpu | \
    awk 'NR<=5 { printf "#%d %s (CPU: %s%%); ", NR, $2, $1 }')
    message+=" Top 5 CPU-consuming processes: $top_processes"
fi

# output
echo "Statistic.cpu_sys_percent:$cpu_sys_percent"
echo "Message.cpu_sys_percent: $message" | tr -d '\n' | paste -sd ''
