#!/bin/bash

: <<'END_COMMENT'
This script checks whether the system time is synchronized with an NTP server,
and also reports the current time offset (if available).

Supports: chronyd, ntpd, systemd-timesyncd
Compatible with: Ubuntu, Debian, RHEL, SLES

Outputs:
- Statistic.ntp_sync: 0 if synced and offset is acceptable, 1 if not
- Message.ntp_sync: detailed synchronization status and offset
END_COMMENT

ntp_sync=1
ntp_message="Time is not synchronized"
offset_message="Offset: unavailable"
statuses_message="Statistic Codes: 0 → OK; 1 → NOK (service not running and/or time not synced or offset too high)"

# max allowed offset (in milliseconds)
OFFSET_MAX=500

# check chronyd
if command -v chronyc >/dev/null 2>&1; then
    leap_status=$(chronyc tracking 2>/dev/null | awk -F: '/^Leap status/ {gsub(/^[ \t]+/, "", $2); print $2}')
    offset_value=$(chronyc tracking 2>/dev/null | awk -F: '/^Root dispersion/ {gsub(/^[ \t]+/, "", $2); print $2}')

    if [[ "$leap_status" == "Normal" ]]; then
        ntp_sync=0
        ntp_message="Time is synchronized via chronyd (Leap status: Normal)"
    else
        ntp_message="chronyd is installed but not synchronized (Leap status: $leap_status)"
    fi

    if [[ -n "$offset_value" ]]; then
        # remove potential "s" or "seconds"
        clean_offset=$(echo "$offset_value" | awk '{gsub(/[a-zA-Z]/, "", $1); print $1}')
        # convert to ms if necessary
        offset_ms=$(awk -v val="$clean_offset" 'BEGIN { printf "%.0f", val * 1000 }')
        offset_message="Offset: ${offset_ms} ms"

        if (( offset_ms > OFFSET_MAX )); then
            ntp_sync=1
            offset_message+=" (too high, threshold ${OFFSET_MAX} ms)"
        fi
    fi

# check systemd-timesyncd
elif command -v timedatectl >/dev/null 2>&1; then
    sync_status=$(timedatectl show -p NTPSynchronized --value 2>/dev/null)

    if [[ "$sync_status" == "yes" ]]; then
        ntp_sync=0
        ntp_message="Time is synchronized via systemd-timesyncd (NTPSynchronized: yes)"
    else
        ntp_message="systemd-timesyncd is not synchronized (NTPSynchronized: $sync_status)"
    fi

    offset_message="Offset: not available (timesyncd does not expose offset directly)"

# check ntpd
elif command -v ntpq >/dev/null 2>&1; then
    sync_line=$(ntpq -pn 2>/dev/null | awk '$1 ~ /^\*/')
    offset_val=$(ntpq -pn 2>/dev/null | awk '$1 ~ /^\*/ {print $9}')

    if [[ -n "$sync_line" ]]; then
        peer=$(echo "$sync_line" | awk '{print $2}')
        ntp_sync=0
        ntp_message="Time is synchronized via ntpd (peer: $peer)"
    else
        ntp_message="ntpd is installed but not currently synchronized with any peer"
    fi

    if [[ -n "$offset_val" ]]; then
        offset_ms=$(awk -v val="$offset_val" 'BEGIN { printf "%.0f", val }')
        offset_message="Offset: ${offset_ms} ms"

        if (( offset_ms > OFFSET_MAX || offset_ms < -OFFSET_MAX )); then
            ntp_sync=1
            offset_message+=" (too high, threshold ${OFFSET_MAX} ms)"
        fi
    fi
else
    ntp_message="No supported NTP client (chronyd, ntpd, or systemd-timesyncd) found"
fi

# output
echo "Statistic.ntp_sync:$ntp_sync"
echo "Message.ntp_sync:$ntp_message. $offset_message. $statuses_message."
