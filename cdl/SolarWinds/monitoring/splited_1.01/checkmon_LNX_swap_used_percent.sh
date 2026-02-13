#!/bin/bash

: <<'END_COMMENT'
This metric shows the percentage of configured swap space that is currently in use.

If no swap is configured, it returns 0 with a message explaining that.
Reads from /proc/meminfo and outputs in SolarWinds-compatible format.
END_COMMENT

# error var to trigger alarm
error_statistic="Statistic.swap_used_percent:100"

# swap state flag
SWAP=false

# safety check
if [[ ! -r /proc/meminfo ]]; then
  echo "$error_statistic"
  echo "Message.swap_used_percent: ERROR: /proc/meminfo is not accessible"
  exit 1
fi

# extract swap info (in KB)
SwapTotal=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)
SwapFree=$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)

# check if swap exists
if [[ -z "$SwapTotal" || "$SwapTotal" -eq 0 ]]; then
  echo "Statistic.swap_used_percent:0"
  echo "Message.swap_used_percent:No SWAP is configured on this system. SWAP configured: [$SWAP]."
  exit 0
fi

SWAP=true
SwapUsed=$((SwapTotal - SwapFree))
swap_used_percent=$((100 * SwapUsed / SwapTotal))

# print output
echo "Statistic.swap_used_percent:$swap_used_percent"
echo "Message.swap_used_percent:Swap used: [$((SwapUsed / 1024))MB]
 of [$((SwapTotal / 1024))MB] total. SWAP configured: [$SWAP]."|tr -d '\n'|paste -sd ''
