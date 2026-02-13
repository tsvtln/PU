#!/bin/bash

: <<'END_COMMENT'
This metric checks if the configured swap size is adequate for the system's total memory.

Rules (based on Red Hat recommendations):
- If MemTotal < 2GB      → swap_opt_size = 2 × MemTotal
- If 2GB ≤ MemTotal < 8GB → swap_opt_size = 60% × MemTotal
- If 8GB ≤ MemTotal < 64GB → swap_opt_size = 4GB
- If MemTotal ≥ 64GB      → swap_opt_size = 8GB

If swap_total ≥ swap_opt_size → OK (0)
Else                          → WARN (2)

If no swap is configured, script prints that and exits with OK (0), assuming no swap is intentional.
END_COMMENT

# alert values (not used for exit code, just for message clarity)
OK=0
WARN=2

# swap config state
SWAP=false

# read memory info
if [[ ! -r /proc/meminfo ]]; then
    echo "Statistic.swap_size_ok:$WARN"
    echo "Message.swap_size_ok: ERROR: /proc/meminfo is not accessible"
    exit 1
fi

# in KB
MemTotal=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
SwapTotal=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)

# check if MemTotal is valid
if [[ -z "$MemTotal" || "$MemTotal" -eq 0 ]]; then
    echo "Statistic.swap_size_ok:$WARN"
    echo "Message.swap_size_ok: ERROR: Invalid MemTotal ('$MemTotal')"
    exit 1
fi

# thresholds (in KB)
mem_2G=$((2 * 1024 * 1024))
mem_4G=$((4 * 1024 * 1024))
mem_8G=$((8 * 1024 * 1024))
mem_64G=$((64 * 1024 * 1024))

# compute optimal swap size (in KB)
if (( MemTotal < mem_2G )); then
    swap_opt_size=$((2 * MemTotal))
elif (( MemTotal >= mem_2G && MemTotal < mem_8G )); then
    swap_opt_size=$((MemTotal * 60 / 100))
elif (( MemTotal >= mem_8G && MemTotal < mem_64G )); then
    swap_opt_size=$mem_4G
else
    swap_opt_size=$((8 * 1024 * 1024))  # 8GB
fi

# If no swap is configured, assume it's intentional
if [[ -z "$SwapTotal" || "$SwapTotal" -eq 0 ]]; then
    echo "Statistic.swap_size_ok:$OK"
    echo "Message.swap_size_ok:No SWAP is configured on this system.
 Skipping optimal swap size check. MemTotal: [$((MemTotal / 1024))MB]."|tr -d '\n'|paste -sd ''
    exit $OK
fi

SWAP=true

# compare and determine status
if (( SwapTotal >= swap_opt_size )); then
    swap_size_ok=$OK
else
    swap_size_ok=$WARN
fi

# print output
echo "Statistic.swap_size_ok:$swap_size_ok"
echo "Message.swap_size_ok:Swap size is [$((SwapTotal / 1024))MB],
 required minimum is [$((swap_opt_size / 1024))MB] based on MemTotal [$((MemTotal / 1024))MB]. SWAP configured: [$SWAP].
 Statistic: Code 0 → OK; Code 2 → swap is not correctly configured." | tr -d '\n' | paste -sd ''
exit $swap_size_ok
