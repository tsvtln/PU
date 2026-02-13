#!/bin/bash

: <<'END_COMMENT'
This metric represents the total system uptime in seconds. Very low uptime may indicate a recent reboot.

```
uptime -p gives output like up 1 day, 2 hours, 10 minutes, useful for dashboards.
we can change thresholds to days/hours by multiplying:
1 day = 86400
1 hour = 3600
```
END_COMMENT

#!/bin/bash

# unused
#WARN_def=600
#CRIT_def=300

# check if /proc/uptime is accessible
if [[ ! -r /proc/uptime ]]; then
    echo "Statistic.server_uptime:999999"
    echo "Message.server_uptime: ERROR: /proc/uptime is not accessible"
    exit 1
fi

# get uptime in seconds (int)
server_uptime=$(awk '{print int($1)}' /proc/uptime)
uptime_days=$((server_uptime / 86400))

# human-readable format for outs
human_uptime=$(uptime -p 2>/dev/null || echo "unknown")

# Output
echo "Statistic.server_uptime:$uptime_days"
echo "Message.server_uptime:Server Uptime: $human_uptime. Statistic shows time in days.
 If too high, consider rebooting the system"|tr -d '\n'|paste -sd ''

# CRIT and WARN are not really used, but possible outcome can be:
#if (( server_uptime < CRIT_def )); then
#    exit 2
#elif (( server_uptime < WARN_def )); then
#    exit 1
#else
#    exit 0
#fi
