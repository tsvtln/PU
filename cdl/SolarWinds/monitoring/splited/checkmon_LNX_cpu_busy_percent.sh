#!/bin/bash

: <<'END_COMMENT'
This metric shows the percentage of CPU time spent doing non-idle work.
It is calculated as: 100 - idle%.

Uses sar to get average CPU idle time from the last 20 minutes.

If sar is not installed or data is missing, an error is printed.
END_COMMENT

# unused
# WARN_def=85
# CRIT_def=90

# check if sar exists
if ! command -v sar >/dev/null; then
  echo "Statistic.cpu_busy_percent:0"
  echo "Message.cpu_busy_percent: ERROR: 'sar' command not found. Please install sysstat."
  exit 1
fi

# figure out which sar file to use
SARFILE=""
if [[ -f /var/log/sa/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sa/sa$(date '+%d')
elif [[ -f /var/log/sysstat/sa$(date '+%d') ]]; then
    SARFILE=/var/log/sysstat/sa$(date '+%d')
else
    echo "Statistic.cpu_busy_percent:0"
    echo "Message.cpu_busy_percent: ERROR: sar file not found for today"
    exit 1
fi

# get avg idle from last 20 minutes
sar_line=$(sar -f "$SARFILE" -s "$(date '+%H:%M:%S' --date='-20min')" | awk '/^Average:/ {print $0}')
cpu_idle=$(echo "$sar_line" | awk '{print $8}' | cut -d'.' -f1)

# validate
if [[ -z "$cpu_idle" || "$cpu_idle" -lt 0 ]]; then
  echo "Statistic.cpu_busy_percent:0"
  echo "Message.cpu_busy_percent: ERROR: Could not parse idle CPU percent from sar."
  exit 1
fi

# calculate busy %
cpu_busy=$((100 - cpu_idle))

# output
echo "Statistic.cpu_busy_percent:$cpu_busy"
echo "Message.cpu_busy_percent:CPU busy time is $cpu_busy%.
 Calculated as 100 - idle ($cpu_idle%). Data based on 20-minute average."|tr -d '\n'|paste -sd ''
