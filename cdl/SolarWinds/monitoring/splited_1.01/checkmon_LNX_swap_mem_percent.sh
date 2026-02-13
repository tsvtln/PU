#!/bin/bash

: <<'END_COMMENT'
This metric shows the percentage of swap used compared to MemAvailable.
It helps evaluate how much the system is relying on swap when memory is tight.

Includes LowWatermark (from /proc/zoneinfo) and page size for deeper insight.
END_COMMENT

# error var to trigger alarm
error_statistic="Statistic.swap_mem_percent:100"

# swap state switch
SWAP=false

# safety check
if [[ ! -r /proc/meminfo ]]; then
  echo "$error_statistic"
  echo "Message.swap_mem_percent: ERROR: /proc/meminfo is not accessible"
  exit 1
fi

# extract values in KB
SwapTotal=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)
SwapFree=$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)
MemAvailable=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

# extract watermark and page size
PAGESIZE=$(getconf PAGESIZE)
MEM_LOWWATERMARK=$(awk '$1 == "low" {sum += $2} END {print sum}' /proc/zoneinfo)
MEM_LOWWATERMARK_KB=$((MEM_LOWWATERMARK * PAGESIZE / 1024))

# default to 0
swap_mem_percent=0

if [[ -n "$SwapTotal" && "$SwapTotal" -gt 0 ]]; then
  SWAP=true
  SwapUsed=$((SwapTotal - SwapFree))

  if [[ -n "$MemAvailable" && "$MemAvailable" -gt 0 ]]; then
    swap_mem_percent=$((100 * SwapUsed / MemAvailable))
  else
    echo "$error_statistic"
    echo "Message.swap_mem_percent: ERROR: Invalid MemAvailable value ('$MemAvailable')"
    exit 1
  fi

  echo "Statistic.swap_mem_percent:$swap_mem_percent"
  echo "Message.swap_mem_percent:Swap used: [$((SwapUsed / 1024))MB] of [$((SwapTotal / 1024))MB] total,
 MemAvailable: [$((MemAvailable / 1024))MB]. SWAP configured: [$SWAP]. LowWatermark: [$((MEM_LOWWATERMARK_KB))KB],
 PageSize: [$((PAGESIZE))B]." | tr -d '\n' | paste -sd ''
else
  # no swap case
  echo "Statistic.swap_mem_percent:0"
  echo "Message.swap_mem_percent:No SWAP configured on this system. MemAvailable: [$((MemAvailable / 1024))MB].
 SWAP configured: [$SWAP]. LowWatermark: [$((MEM_LOWWATERMARK_KB))KB],
 PageSize: [$((PAGESIZE))B]." | tr -d '\n' | paste -sd ''
fi
