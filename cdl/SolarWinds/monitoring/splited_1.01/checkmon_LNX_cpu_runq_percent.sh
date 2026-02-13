#!/bin/bash

: <<'END_COMMENT'
RUNQ % needs:
CPU count
run queue from sar -q
calculate cpu_runq_percent = 100 * runq / cpu_nb
print metric and message
END_COMMENT


# variables
# WARN_def=125
# CRIT_def=150

