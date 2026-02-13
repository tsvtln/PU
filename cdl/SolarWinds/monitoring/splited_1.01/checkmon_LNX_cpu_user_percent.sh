#!/bin/bash

: <<'END_COMMENT'
read sar -u data (not -q)
get the 3rd column of the Average: line
format and print with thresholds and explanation

This metric refers to the percentage of time the CPU spent executing processes in user space
(applications, scripts, etc.). High values may indicate heavy user-side computation.
END_COMMENT

# stat to trigger alarm
error_statistic="Statistic.cpu_user_percent:100"

# checking if sar exists
if ! command -v sar >/dev/null; then
    echo "$error_statistic"
    echo "Message.cpu_user_percent: Unable to find 'sar' command - please check and install it on the target server." | tr -d '\n' | paste -sd ''
    exit 1
fi

# determine sar file location
SARFILE=""
if [[ -f /var/log/sa/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sa/sa$(date '+%d')
elif [[ -f /var/log/sysstat/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sysstat/sa$(date '+%d')
else
    echo "$error_statistic"
    echo "Message.cpu_user_percent: ERROR: 'sar' command not found.
 Please install and configure sysstat. Make sure services are enabled afterwards."|tr -d '\n'|paste -sd ''
    exit 1
fi

# get user CPU % from 3rd column
sar_cpu_avg_line=$(sar -u -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/ { print $0 }')
cpu_user_percent=$(echo "$sar_cpu_avg_line" | awk '{print $3}' | cut -d'.' -f1)

# default message
message="Current CPU usage by user processes: $cpu_user_percent%. High values may indicate heavy user-side computation."

# if user CPU ≥ 90%, add top 5 user-space processes (excluding kernel/system)
if [[ $cpu_user_percent -ge 90 ]]; then
    top_processes=$(ps -eo pcpu,comm --sort=-pcpu | \
        grep -vE '^( *[0-9.]+ +)?(kworker|migration|rcu_|watchdog|kauditd|ksoftirqd|kdevtmpfs|kswapd|khugepaged)' | \
        awk 'NR<=5 { printf "#%d %s (CPU: %s%%); ", NR, $2, $1 }')

    if [[ -z "$top_processes" ]]; then
        top_processes="No user processes found"
    fi

    message+=" Top 5 CPU-consuming user processes: $top_processes"
fi

# output
echo "Statistic.cpu_user_percent:$cpu_user_percent"
echo "Message.cpu_user_percent: $message" | tr -d '\n' | paste -sd ''
