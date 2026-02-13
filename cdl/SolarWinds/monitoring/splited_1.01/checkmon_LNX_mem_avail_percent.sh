#!/bin/bash

: <<'END_COMMENT'
This metric represents the percentage of total memory that is available for
allocation to processes (MemAvailable). A low value indicates high memory pressure.

Reads /proc/meminfo
Extracts MemTotal and MemAvailable
Calculates simple % available RAM
If memory is ≤10%, prints top 5 memory-consuming processes (excluding kernel/system).
RSS = Resident Set Size (memory used)
END_COMMENT

# error var to trigger alarm
error_statistic="Statistic.mem_avail_percent:0"

# swap switch
SWAP=false

# safety check
if [[ ! -r /proc/meminfo ]]; then
  echo "$error_statistic"
  echo "Message.mem_avail_percent: ERROR: /proc/meminfo is not accessible. Check permissions and file existence."
  exit 1
fi

# extract values (KB)
MemTotal=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
MemAvailable=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

if [[ -z "$MemTotal" || "$MemTotal" -eq 0 ]]; then
  echo "$error_statistic"
  echo "Message.mem_avail_percent: ERROR: MemTotal is invalid ('$MemTotal')"
  exit 1
fi

# check and include swap
SwapTotal=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)
SwapAvailable=$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)

if [[ "$SwapTotal" -gt 0 ]]; then
  SWAP=true
  MemTotal=$((MemTotal + SwapTotal))
  MemAvailable=$((MemAvailable + SwapAvailable))
fi

# calculate percentage
mem_avail_percent=$((100 * MemAvailable / MemTotal))

# base message
message="Available Memory [$((MemAvailable / 1024))MB] out of [$((MemTotal / 1024))MB] total. SWAP configured state [$SWAP]."

# if memory low, get top 5 memory-consuming processes
if [[ "$mem_avail_percent" -le 10 ]]; then
  top_mem_procs=$(ps --sort=-rss -eo rss,comm --no-headers | \
    awk 'NR<=5 { printf "#%d %s (RSS: %.1fMB); ", NR, $2, $1/1024 }')

  if [[ -z "$top_mem_procs" ]]; then
    top_mem_procs="No processes found"
  fi

  message+=" Top memory-consuming processes: $top_mem_procs"
fi

# output
echo "Statistic.mem_avail_percent:$mem_avail_percent"
echo "Message.mem_avail_percent:$message" | tr -d '\n' | paste -sd ''