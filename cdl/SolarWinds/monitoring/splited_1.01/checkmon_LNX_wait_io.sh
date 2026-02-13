#!/bin/bash

: <<'END_COMMENT'
Time, in percentages, spent waiting for input/output (IO) operations.
Note: Use the lowest threshold possible.
If CPU waits IO is high, there may be problems with hard disk or problems with accessing NFS shares (if you use NFS).
END_COMMENT

# var to trigger alarm on error
statistic_error="Statistic.wait_io:100"

# run vmstat and capture output
vmstat_out=$(LC_ALL=C vmstat)

# ensure vmstat output has enough lines
lines_count=$(echo "$vmstat_out" | wc -l)
if (( lines_count < 3 )); then
    echo "$statistic_error"
    echo "Message.wait_io: ERROR:vmstat output too short."
    exit 1
fi

# extract the header and data lines
header_line=$(echo "$vmstat_out" | sed -n 2p)
data_line=$(echo "$vmstat_out" | sed -n 3p)

# convert header and data into arrays
read -ra header <<< "$header_line"
read -ra data <<< "$data_line"

# find the index of "wa"
wa_index=-1
for i in "${!header[@]}"; do
    if [[ "${header[$i]}" == "wa" ]]; then
        wa_index=$i
        break
    fi
done

# output the stat or error
if (( wa_index >= 0 )); then
    wa_value="${data[$wa_index]}"
    echo "Statistic.wait_io: $wa_value"
    echo "Message.wait_io: cpu wait io in percentage: $wa_value"
    exit 0
else
    echo "$statistic_error"
    echo "Message.wait_io: ERROR: can't find cpu wait io (wa) in output of -vmstat- command."
    exit 1
fi
