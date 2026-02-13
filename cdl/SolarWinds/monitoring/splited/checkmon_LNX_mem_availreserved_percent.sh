#!/bin/bash

: <<'END_COMMENT'
This metric represents the percentage of total memory that is available for
  allocation to processes (MemAvailable). A low value indicates high memory pressure.

The metric is a computed value MEMAVAILABLERESERVED/mem_total*100

(MEMAVAILABLERESERVED = mem_avail - MEM_LOWWATERMARK if enough swap available
 (> MEM_LOWWATERMARK), otherwise it is mem_avail)

([mem_avail={value}]: Available memory in KB)
([mem_total={value}]: Total memory in KB)
([MEM_LOWWATERMARK={value}]: Low water mark threshold across memory zones)
END_COMMENT

# swap switch
SWAP=false

if [[ ! -r /proc/meminfo ]]; then
  echo "Statistic.mem_availreserved_percent:0"
  echo "Message.mem_availreserved_percent:
 ERROR: /proc/meminfo is not accessible. Check permissions and file existence."| tr -d '\n' | paste -sd ''
  exit 1
fi

MemTotal=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
MemAvailable=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

if [[ -z "$MemTotal" || "$MemTotal" -eq 0 ]]; then
  echo "Statistic.mem_availreserved_percent:0"
  echo "Message.mem_availreserved_percent: ERROR: MemTotal is an invalid value ('$MemTotal')"
  exit 1
fi

# check swap
SwapTotal=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)
SwapAvailable=$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)

if [[ "$SwapTotal" -gt 0 ]]; then
  MemTotal=$((MemTotal + SwapTotal))
  MemAvailable=$((MemAvailable + SwapAvailable))
  SWAP=true
fi

# low watermark
PAGESIZE=$(getconf PAGESIZE)
MEM_LOWWATERMARK=$(($(awk '$1 == "low" {sum += $2} END {print sum}' /proc/zoneinfo) * PAGESIZE / 1024))
MEMINFO_SRECLAIMABLE=$(awk '/^SReclaimable:/ {print $2}' /proc/meminfo)
# those are not used, but keeping them here if needed in the future
#MEMMINFO_MEMTOT=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
#MEMINFO_MEMFREE=$(awk '/^MemFree:/ {print $2}' /proc/meminfo)
#MEMINFO_FILE=$(cat /proc/meminfo | \
#  awk '{MEMINFO[$1]=$2} END {print (MEMINFO["Active(file):"] + MEMINFO["Inactive(file):"])}')

if $SWAP && [[ "$SwapTotal" -gt "$MEM_LOWWATERMARK" ]]; then
  MemAvailable=$((MemAvailable - MEM_LOWWATERMARK))
fi

mem_availreserved_percent=$((100 * MemAvailable / MemTotal))

# build base message
message="Available Memory [$((MemAvailable / 1024))MB] out of [$((MemTotal / 1024))MB] total.
 SWAP configured state [$SWAP]. LowWatermark: [$((MEM_LOWWATERMARK / 1024))MB].
 PAGESIZE: [$PAGESIZE KB]. Reclaimable memory: [$((MEMINFO_SRECLAIMABLE / 1024))MB]."

# if memory critically low, include top 5 memory-consuming processes
if [[ "$mem_availreserved_percent" -le 10 ]]; then
  top_processes=$(ps --sort=-rss -eo rss,comm --no-headers | \
    awk 'NR<=5 { printf "#%d %s (RSS: %.1fMB); ", NR, $2, $1/1024 }')

  if [[ -z "$top_processes" ]]; then
    top_processes="No processes found"
  fi

  message+=" Top memory-consuming processes: $top_processes"
fi

# Output
echo "Statistic.mem_availreserved_percent:$mem_availreserved_percent"
echo "Message.mem_availreserved_percent:$message" | tr -d '\n' | paste -sd ''
