#!/bin/bash

: <<'END_COMMENT'
This counts all processes whose status starts with Z.
A value of 0 is good.
If the number rises, it could indicate:
Parent processes are not cleaning up zombies (wait() call not made).
Application issues or badly written daemon forks.

The metric reports the number of zombie processes
(defunct processes that have completed but still occupy an entry in the process table).
Zombies may indicate misbehaving parent processes.
END_COMMENT

# unused
#WARN_def=1
#CRIT_def=5

# count zombie processes
proc_zombie=$(ps -eo stat | grep -c '^Z')

# outputs
echo "Statistic.proc_zombie:$proc_zombie"
echo "Message.proc_zombie:Current number of zombies: $proc_zombie. A value of 0 is good.
If the number rises, it could indicate:
Parent processes are not cleaning up zombies (wait() call not made).
Application issues or badly written daemon forks."|tr -d '\n'|paste -sd ''
