#!/bin/bash

#================= MONITOR FUNCTION BEGIN

checkmon_LNX_mem_ALL(){
        # Display multiple statistics related to MEM metrics
        get_mem_use

        print_stat "$LIST_METRICS_MEM"
}

checkmon_LNX_cpu_ALL(){
        # Display multiple statistics related to CPU metrics
        get_cpu_use

        print_stat "$LIST_METRICS_CPU"
}

checkmon_LNX_mem_total(){
        # Display single statistic for mem_total metrics
        get_mem_use

        print_stat "mem_total"
}

checkmon_LNX_mem_used(){
        # Display single statistic for mem_used metrics
        get_mem_use

        print_stat "mem_used"
}

checkmon_LNX_mem_avail(){
        # Display single statistic for mem_avail metrics
        get_mem_use

        print_stat "mem_avail"
}

checkmon_LNX_mem_avail_percent(){
        # Display single statistic for mem_avail_percent metrics
        get_mem_use

        WARN_def=15
        CRIT_def=10

        echo_debug "ALERT => mem_avail_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "mem_avail_percent"
}

checkmon_LNX_mem_availreserved_percent(){
        # Display single statistic for mem_avail metrics
        get_mem_use

        WARN_def=10
        CRIT_def=5

        echo_debug "ALERT => mem_availreserved_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "MEMAVAILABLERESERVED_PERCENT"
}

checkmon_LNX_swap_total(){
        # Display single statistic for swap_total metrics
        get_mem_use

        print_stat "swap_total"
}

checkmon_LNX_swap_used(){
        # Display single statistic for swap_used metrics
        get_mem_use

        swap_used_message='This metric refers to the swap used in Kb'

        print_stat "swap_used"
}

checkmon_LNX_swap_used_percent(){
        # Display single statistic for swap_used_percent metrics
        get_mem_use

        WARN_def=65
        CRIT_def=75
        echo_debug "ALERT => swap_use_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "swap_used_percent"
}

checkmon_LNX_swap_mem_percent(){
        # Display single statistic for swap_mem_percent metrics
        get_mem_use

        WARN_def=85
        CRIT_def=95
        echo_debug "ALERT => swap_mem_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "swap_mem_percent"
}

checkmon_LNX_swap_opt_size(){
        # Display single statistic for swap_opt_size metrics
        get_mem_use

        print_stat "swap_opt_size"
}

checkmon_LNX_swap_size_ok(){
        # Display single statistic for swap_size_ok metrics
        get_mem_use

        WARN_def=2
        CRIT_def=3
        echo_debug "ALERT => swap_size_ok => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "swap_size_ok"
}

checkmon_LNX_cpu_user_percent(){
        # Display single statistic for cpu_user_percent metrics
        get_cpu_use

        WARN_def=85
        CRIT_def=90
        echo_debug "ALERT => cpu_user_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_user_percent"
}

checkmon_LNX_cpu_sys_percent(){
        # Display single statistic for cpu_sys_percent metrics
        get_cpu_use

        WARN_def=85
        CRIT_def=90
        echo_debug "ALERT => cpu_sys_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_sys_percent"
}

checkmon_LNX_cpu_busy_percent(){
        # Display single statistic for cpu_busy_percent metrics
        get_cpu_use

        WARN_def=85
        CRIT_def=90
        echo_debug "ALERT => cpu_busy_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_busy_percent"
}

checkmon_LNX_cpu_wait_percent(){
        # Display single statistic for cpu_wait_percent metrics
        get_cpu_use

        print_stat "cpu_wait_percent"
}

checkmon_LNX_cpu_idle_percent(){
        # Display single statistic for cpu_idle_percent metrics
        get_cpu_use

        print_stat "cpu_idle_percent"
}

checkmon_LNX_cpu_nb(){
        # Display single statistic for cpu_nb metrics
        get_cpu_use

        print_stat "cpu_nb"
}

checkmon_LNX_cpu_runq(){
        # Display single statistic for cpu_runq metrics
        get_cpu_use

        print_stat "cpu_runq"
}

checkmon_LNX_cpu_runq_percent(){
        # Display single statistic for cpu_runq_percent metrics
        get_cpu_use

        WARN_def=125
        CRIT_def=150
        echo_debug "ALERT => cpu_runq_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_runq_percent"
}

checkmon_LNX_cpu_loadavg1(){
        # Display single statistic for cpu_loadavg1 metrics
        get_cpu_use

        print_stat "cpu_loadavg1"
}

checkmon_LNX_cpu_loadavg1_canon_percent(){
        # Display single statistic for cpu_loadavg1_canon_percent metrics
        get_cpu_use

        WARN_def=125
        CRIT_def=150
        echo_debug "ALERT => cpu_loadavg1_canon_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_loadavg1_canon_percent"
}

checkmon_LNX_cpu_loadavg5(){
        # Display single statistic for cpu_loadavg5 metrics
        get_cpu_use

        print_stat "cpu_loadavg5"
}

checkmon_LNX_cpu_loadavg5_canon_percent(){
        # Display single statistic for cpu_loadavg5_canon_percent metrics
        get_cpu_use

        WARN_def=125
        CRIT_def=150
        echo_debug "ALERT => cpu_loadavg5_canon_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_loadavg5_canon_percent"
}

checkmon_LNX_cpu_loadavg15(){
        # Display single statistic for cpu_loadavg15 metrics
        get_cpu_use

        print_stat "cpu_loadavg15"
}

checkmon_LNX_cpu_loadavg15_canon_percent(){
        # Display single statistic for cpu_loadavg15_canon_percent metrics
        get_cpu_use

        WARN_def=125
        CRIT_def=150
        echo_debug "ALERT => cpu_loadavg15_canon_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        print_stat "cpu_loadavg15_canon_percent"
}

checkmon_LNX_server_uptime(){
        # Display single statistic for server_uptime metrics

        WARN_def=365
        CRIT_def=500
        echo_debug "ALERT => server_uptime => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        server_uptime=$(uptime | awk '{print $3}')
        server_uptime_message='This metric show the number of days since last reboot.'

        print_stat "server_uptime"
}

checkmon_LNX_proc_zombie(){
        # Display single statistic for zombie_proc metrics

        #check if exists zombies processes ... not good for system is there are too much
        #if found need to investigate and if possible kill them by killing their father

        WARN_def=10
        CRIT_def=15
        echo_debug "ALERT => zombie_proc => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        zombie_proc=$(ps aux | awk '
                BEGIN{z=0}
                $8~/Z/{z=1+z}
                END{print z}'
                )

        export zombie_proc_message='That metric refers to the number of zombie process currently running on the system.'

        print_stat "zombie_proc"
}

checkmon_LNX_fs_inode_max_percent(){
        # Display single statistic for max_inode_percent metrics

        #this metric return the maximum inode percent usage among all the current file-systems
        #that it is due to a limitation of Solarwinds which do not managed correctly dynamic statistics

        WARN_def=80
        CRIT_def=95
        echo_debug "ALERT => max_inode_percent => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        #max_inode=$(sar -F 1 $MAX_SAR_COUNT | awk '/^Summary/&&!/FILESYSTEM$/{if($8>inode_max){inode_max=$8;fs=$NF}}END{print inode_max"|"fs}')
        max_inode=$(df -Pli | awk 'BEGIN{inode_max=0}!/^Filesystem/&&$5~/%/{gsub(/%/,"",$5);if($5>inode_max){inode_max=$5;fs=$NF}}END{print inode_max"|"fs}')

        max_inode_percent=$(echo $max_inode | cut -d'|' -f1 | cut -d'.' -f1)
        max_inode_fs=$(echo $max_inode | cut -d'|' -f2)

        max_inode_percent_message="That metric refers to the inode percent usage of the file-system fs=$max_inode_fs among all the local current file-systems"

        print_stat "max_inode_percent"
}

checkmon_LNX_service(){
        # Display single statistic for service_status metrics

        #check if given service is active and running

        arg=$*
        service_name=${arg:="default"}

        SERVICE_SYSTEM_LIST_RHEL7="auditd chronyd crond sshd firewalld postfix rsyslog tuned"
        SERVICE_SYSTEM_LIST_RHEL6="auditd crond iptables ntpd rsyslog sshd"
        SERVICE_SYSTEM_LIST_DEBIAN="cron sshd rsyslog"
        SERVICE_SYSTEM_LIST_SLES="auditd chronyd cron sshd rsyslog tuned"

        SERVICE_SYSTEM_LIST_VIRTUAL_RHEL7="vmtoolsd"
        SERVICE_SYSTEM_LIST_VIRTUAL_RHEL6="vmware-tools"                    # open-vm-tools not supported on RHEL6
        SERVICE_SYSTEM_LIST_VIRTUAL_DEBIAN="vmware-tools"
        SERVICE_SYSTEM_LIST_VIRTUAL_DEBIAN7="vmware-tools"

        if [[ $ostype == "rhel" && $osver_major -ge 7  ]]; then
                SERVICE_SYSTEM_LIST=$SERVICE_SYSTEM_LIST_RHEL7
                SERVICE_SYSTEM_LIST_VIRTUAL=$SERVICE_SYSTEM_LIST_VIRTUAL_RHEL7
        elif [[ $ostype == "rhel" && $osver_major -lt 7 ]]; then
                SERVICE_SYSTEM_LIST=$SERVICE_SYSTEM_LIST_RHEL6
                SERVICE_SYSTEM_LIST_VIRTUAL=$SERVICE_SYSTEM_LIST_VIRTUAL_RHEL6
        elif [[ $ostype == "debian" && $osver_major -gt 7 ]]; then
                SERVICE_SYSTEM_LIST=$SERVICE_SYSTEM_LIST_DEBIAN
                SERVICE_SYSTEM_LIST_VIRTUAL=$SERVICE_SYSTEM_LIST_VIRTUAL_DEBIAN
        elif [[ $ostype == "debian" && $osver_major -le 7 ]]; then
                SERVICE_SYSTEM_LIST=$SERVICE_SYSTEM_LIST_DEBIAN
                SERVICE_SYSTEM_LIST_VIRTUAL=$SERVICE_SYSTEM_LIST_VIRTUAL_DEBIAN7
        elif [[ $ostype == *sles* && $osver_major -ge 15 ]]; then
                SERVICE_SYSTEM_LIST=$SERVICE_SYSTEM_LIST_SLES
        fi

        if [ "$machine_type" == "virtual" ]; then
                echo_debug "virtual machine adding SERVICE_SYSTEM_LIST_VIRTUAL=$SERVICE_SYSTEM_LIST_VIRTUAL"
                SERVICE_SYSTEM_LIST="$SERVICE_SYSTEM_LIST $SERVICE_SYSTEM_LIST_VIRTUAL"
        else
                echo_debug "physical machine"
        fi

        if [ -f $MONITORED_SVC ]; then
                echo_debug "checking INCLUDE list MONITORED_SVC=$MONITORED_SVC\n$(cat $MONITORED_SVC)"
                for service in $(cat $MONITORED_SVC); do
                        echo_debug "Adding service=$service in monitored list as listed in MONITORED_SVC=$MONITORED_SVC"
                        SERVICE_SYSTEM_LIST="$SERVICE_SYSTEM_LIST $service"
                done
        fi

        if [ -f $NOT_MONITORED_SVC ]; then
                echo_debug "checking EXCLUDE list NOT_MONITORED_SVC=$NOT_MONITORED_SVC\n$(cat $NOT_MONITORED_SVC)"
        fi

        declare -A service_tab

        WARN_def=$WARN_alert
        CRIT_def=$CRIT_alert
        echo_debug "ALERT => service_status => default thresholds should be WARN_def=$WARN_def, CRIT_def=$CRIT_def"

        if [ "$service_name" == "" ]; then
                echo "#ERROR : monitor 'checkmon_LNX_running_service' require a service given as parameter"
                usage
        elif [ "$service_name" == "default" ]; then
                service_list="$SERVICE_SYSTEM_LIST"
        else
                service_list="$service_name"
        fi

        echo_debug "checking system services service_list=$service_list"

        max_value=0
        sum_value=0
        max_key=''
        service_name_enable=''
        for service_name in $service_list; do
                if [[ -f $NOT_MONITORED_SVC && $(egrep "^${service_name}$" -c $NOT_MONITORED_SVC) -ne 0 ]]; then
                        echo_debug "skip service_name=${service_name} as listed in the NOT_MONITORED_SVC=$NOT_MONITORED_SVC list"
                        continue
                fi
                if [[ ( $ostype == "rhel" && $osver_major -ge 7 ) || ($ostype == "debian" && $osver_major -gt 7) ]]; then
                        service_name_enable=$(systemctl --no-pager list-unit-files | awk '$1~/^'"$service_name"'.service$/{print $2}')
                        if [  "$service_name_enable" == "" ]; then
                                echo_debug "#WARNING : monitor 'checkmon_LNX_running_service' : the service_name=$service_name do not exists"
                                service_status=$CRIT_alert
                        elif [  "$service_name_enable" == "enabled" ]; then
                                echo_debug "checking status of service_name=$service_name"
                                service_status=$(sudo systemctl status $service_name 2>&1 |
                                        awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                                /Active:/{if(match($0,/running/)){print ok}else{print crit}}
                                                /CGroup:/{exit}
                                                '
                                )
                        else
                                echo_debug "service_name=$service_name is not enable => service_name_enable=$service_name_enable"
                                service_status=0
                        fi

                elif [[ $ostype == "debian" && $osver_major -le 7 ]]; then
                        service_name_enable=$(ls -F /etc/init.d/ | grep '*$' | awk '/^'"$service_name"'*/{print "enable"}')
                        if [  "${service_name_enable}" == "" ]; then
                                echo_debug "#WARNING : monitor 'checkmon_LNX_running_service' : the service_name=$service_name do not exists"
                                service_status=$CRIT_alert
                        elif [  "$service_name_enable" == "enabled" ]; then
                                echo_debug "checking status of service_name=$service_name"
                                service_status=$(sudo /etc/init.d/${service_name} status 2>&1 |
                                        awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                               BEGIN{alert_status=crit}
                                               /running/{alert_status=ok}
                                               END{print alert_status}'
                                )
                        else
                                echo_debug "service_name=$service_name is not enable => service_name_enable=$service_name_enable"
                                service_status=0
                        fi

                elif [[ $ostype == "rhel" && $osver_major -lt 7 ]]; then
                        if [[ -f /etc/rc.d/init.d/${service_name} || -f /etc/${service_name}/services.sh ]]; then
                                if [[ -f /etc/init/${service_name}.conf ]]; then
                                        echo_debug "checking status of service_name=$service_name"
                                        service_status=$(sudo /etc/${service_name}/services.sh status 2>&1 |
                                                awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                                BEGIN{alert_status=crit}
                                                /running/{alert_status=ok}
                                                END{print alert_status}'
                                        )
                                elif [[ -f /etc/rc.d/init.d/${service_name} ]]; then
                                        #check if service should be running at runlevel=3
                                        service_name_enable=$(chkconfig --list $service_name | awk '{split($5,e,":");print e[2]}')
                                        if [  "$service_name_enable" == "on" ]; then
                                                service_status=$(sudo service $service_name status 1>/dev/null 2>&1;echo $? |
                                                        awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                                                /^0$/{print ok}
                                                                !/^0$/{print crit}
                                                                '
                                                        )
                                        else
                                                echo_debug "service_name=$service_name is not enable => service_name_enable=$service_name_enable"
                                                service_status=0
                                        fi
                                fi
                        else
                                echo_debug "#WARNING : monitor 'checkmon_LNX_running_service' : the service_name=$service_name do not exists"
                                service_status=$CRIT_alert
                        fi

                if [[ ($ostype == *sles* && $osver_major -ge 15) ]]; then
                        service_name_enable=$(systemctl --no-pager list-unit-files | awk '$1~/^'"$service_name"'.service$/{print $2}')
                        if [  "$service_name_enable" == "" ]; then
                                echo_debug "#WARNING : monitor 'checkmon_LNX_running_service' : the service_name=$service_name do not exists"
                                service_status=$CRIT_alert
                        elif [  "$service_name_enable" == "enabled" ]; then
                                echo_debug "checking status of service_name=$service_name"
                                service_status=$(sudo systemctl status $service_name 2>&1 |
                                        awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                                /Active:/{if(match($0,/running/)){print ok}else{print crit}}
                                                /CGroup:/{exit}
                                                '
                                )
                        else
                                echo_debug "service_name=$service_name is not enable => service_name_enable=$service_name_enable"
                                service_status=0
                        fi
                fi
        fi

                service_tab[$service_name]=$service_status
                echo_debug "service_name=$service_name service_status=$service_status - service_tab[$service_name]=${service_tab[$service_name]}"

                for key in "${!service_tab[@]}"; do
                        echo_debug "looking at service_tab[$key]=${service_tab[$key]} - max_value=$max_value"
                        if [ ${service_tab[$key]} -ge $max_value ]; then
                                max_key=$key
                                max_value="${service_tab[$max_key]}"
                                sum_value=$((sum_value+${service_tab[$max_key]}))
                        fi
                done
        done

        echo_debug "max_value=$max_value - max_key=$max_key - sum_value=$sum_value"

        if [ $sum_value -gt 0 ]; then
                #at lease one checked service is NOT OK
                service_status_caption="service [$max_key] has a NOT OK status"
        else
                #all checked services are OK
                service_status_caption="all checked service have OK status"
        fi

        service_status=$max_value
        service_status_message="That metric refers to that $service_status_caption among checked_service_name : [$service_list] => service_status = $OK_alert => running ; service_status = $CRIT_alert => not_running"

        print_stat "service_status"
}

#================= MONITOR FUNCTION END

#================= METRIC FUNCTION BEGIN
get_mem_use(){
        # Function to gather both memory and swap usage

        LIST_METRICS_MEM="mem_total,mem_used,mem_avail,mem_avail_percent,swap_total,swap_used,swap_used_percent,
         swap_mem_percent,swap_opt_size,swap_size_ok,MEM_LOWWATERMARK,COMPUTED_MEMINFO_MEMAVAILABLE,
         MEMAVAILABLERESERVED,MEMAVAILABLERESERVED_PERCENT"

        # Gather mem related metrics

        mem_total=$(free -k | awk '/^Mem:/{print $2}')
        mem_used=$(free -k | awk '/^Mem:/{print $3}')
        if [[ ( $ostype == "rhel" && $osver_major -ge 7 ) || $ostype == "debian" ]]; then
                mem_avail=$(free -k | awk '/^Mem:/{print $NF}')
        elif [[ $ostype == "rhel" && $osver_major -lt 7 ]]; then
                mem_avail=$(free -k | awk -v min_free=$(cat /proc/sys/vm/min_free_kbytes) '/^Mem:/{print $4+$NF-min_free}')
        elif [[ $ostype == *sles* ]]; then
                mem_avail=$(free -k | awk '/^Mem:/{print $NF}')
        else
                mem_avail=""
        fi
        if [ "$mem_avail" == "" ]; then
                mem_avail_percent=""
        else
                mem_avail_percent=$((100*mem_avail/mem_total))
        fi

        mem_total_message='This metric refers to the total memory in Kb configured'
        mem_used_message='This metric refers to the memory used in Kb (NOT including cache and buffer)'
        mem_avail_message='This metric refers to the available memory in Kb
         (for RHEL6 it is the sum of free+cache-min_free / for RHEL7+ and Debian, it refers to
          availaible mem which is the estimated amount of memory usabled by new application after releasing
           eventually some memory pages used for cache)'
        mem_avail_percent_message="This metric is a computed value showing the
         percentage of available memory = mem_avail/mem_total*100
          ([mem_avail=$mem_avail]:$mem_avail_message) ([mem_total=$mem_total]:$mem_total_message)"

        # Gather swap related metrics

        swap_total=$(free -k | awk '/^Swap:/{print $2}')
        swap_used=$(free -k | awk '/^Swap:/{print $3}')
        swap_free=$(free -k | awk '/^Swap:/{print $4}')
        swap_used_percent=$((100*swap_used/swap_total))
        swap_mem_percent=$((100*swap_used/mem_avail))

        swap_total_message='This metric refers to the total swap in Kb configured'
        swap_used_percent_message='This metric is a computed value showing the percentage of used swap = swap_used/swap_total*100'
        swap_mem_percent_message='This metric is a computed value showing the percentage of used swap compared to the mem_avail = swap_used/mem_avail*100'

        #Compute reserved memory and deducte available memory

        ####As available field from free command shows only the portion of available mem preventing the system to swap, it is not very accurate to configure a monitoring treshold ... so we add the memory reserved by the kernel with the low watermark. Of course setting a threshold on this value will only make sens if there are space available in swap!
        #https://access.redhat.com/support/cases/#/case/02852147
        #https://unix.stackexchange.com/questions/261247/how-can-i-get-the-amount-of-available-memory-portably-across-distributions

        PAGESIZE=$(getconf PAGESIZE)
        MEM_LOWWATERMARK=$(($(awk '$1 == "low" {LOW_WATERMARK += $2} END {print LOW_WATERMARK }' /proc/zoneinfo) * PAGESIZE / 1024))

        MEMINFO=$(</proc/meminfo)

        MEMINFO_MEMTOT=$(echo "${MEMINFO}" | awk '$1 == "MemTotal:" {print $2}')
        MEMINFO_MEMFREE=$(echo "${MEMINFO}" | awk '$1 == "MemFree:" {print $2}')
        MEMINFO_FILE=$(echo "${MEMINFO}" | awk '{MEMINFO[$1]=$2} END {print (MEMINFO["Active(file):"] + MEMINFO["Inactive(file):"])}')
        MEMINFO_SRECLAIMABLE=$(echo "${MEMINFO}" | awk '$1 == "SReclaimable:" {print $2}')

        COMPUTED_MEMINFO_MEMAVAILABLE=$((
        MEMINFO_MEMFREE - MEM_LOWWATERMARK
        + MEMINFO_FILE - ((MEMINFO_FILE/2) < MEM_LOWWATERMARK ? (MEMINFO_FILE/2) : MEM_LOWWATERMARK)
        + MEMINFO_SRECLAIMABLE - ((MEMINFO_SRECLAIMABLE/2) < MEM_LOWWATERMARK ? (MEMINFO_SRECLAIMABLE/2) : MEM_LOWWATERMARK)
        ))

        if [[ "${COMPUTED_MEMINFO_MEMAVAILABLE}" -le 0 ]]; then
                COMPUTED_MEMINFO_MEMAVAILABLE=0
        fi

        if [ $MEM_LOWWATERMARK -lt $swap_free ]; then
                MEMAVAILABLERESERVED=$((mem_avail+MEM_LOWWATERMARK))
        else
                MEMAVAILABLERESERVED=$mem_avail
        fi

        MEMAVAILABLERESERVED_PERCENT=$((100*MEMAVAILABLERESERVED/mem_total))

        MEM_LOWWATERMARK_message="This metric represent the sum of the low water mark of the diffent memory zones"
        COMPUTED_MEMINFO_MEMAVAILABLE_message="This metric is a computiong value to estimate the available memory using the same alogorythme than available field from free command"
        MEMAVAILABLERESERVED_message="This metric is a computed value mem_avail-MEM_LOWWATERMARK if enough swap available (>MEM_LOWWATERMARK) otherwise it is mem_avail ([mem_avail=$mem_avail]:$mem_avail_message) ([mem_total=$mem_total]:$mem_total_message) ([MEM_LOWWATERMARK=$MEM_LOWWATERMARK]:$MEM_LOWWATERMARK_message)"
        MEMAVAILABLERESERVED_PERCENT_message="This metric is a computed value MEMAVAILABLERESERVED/mem_total*100 (MEMAVAILABLERESERVED=$MEMAVAILABLERESERVED_message)"

        # Determine the optiomal Swap size

                #https://access.redhat.com/solutions/45192
                #swap size need to be configured based on total memory of the system
                #if mem < 2G => swap should be 2*mem
                #if 2G < mem < 8G => swap should be 60% mem
                #if mem > 8G => swap should be 4G
                #if mem > 64G => swap should be 8G

        swap_opt_size_message='This metric is a computed value showing the optimal swap size to be configured on the system based on the following rules : if mem_total<2Gb => swap_opt_size=$((2*$mem_total); if 2Gb<=mem_total<8Gb => swap_opt_size=$((60%*$mem_total); if 8Gb<=mem_total<64Gb => swap_opt_size=4Gb; if 64Gb<=mem_total => swap_opt_size=8Gb'
        swap_size_ok_message="This metric shows if the current swap size is correctly configured compared to the computed swap_opt_size : $OK_alert is OK, $WARN_alert is BAD"

        mem_2G=$((2*1024*1024))
        mem_4G=$((4*1024*1024))
        mem_8G=$((8*1024*1024))
        mem_64G=$((64*1024*1024))

        if [ $mem_total -le $mem_2G ]; then
                swap_opt_size=$((2*$mem_total))
        elif [ $mem_total -gt $mem_2G ] && [ $mem_total -le $mem_8G ]; then
                swap_opt_size=$((${mem_total}*60/100))
        elif [ $mem_total -gt $mem_8G ] && [ $mem_total -le $mem_64G ]; then
                swap_opt_size=$mem_4G
        elif [ $mem_total -gt $mem_64G ]; then
                swap_opt_size=$mem_8G
        fi
        if [ $swap_total -ge $swap_opt_size ]; then
                swap_size_ok=$OK_alert
        else
                swap_size_ok=$WARN_alert
        fi

        check_metric_not_empty "$LIST_METRICS_MEM"
}

get_cpu_use(){
        # Function to check CPU usage and CPU run queue

        LIST_METRICS_CPU="cpu_user_percent,cpu_sys_percent,cpu_wait_percent,cpu_busy_percent,cpu_idle_percent,cpu_runq,cpu_runq_percent,cpu_loadavg1,cpu_loadavg5,cpu_loadavg15"

        # Gather CPU related metrics

        cpu_user_percent_message='This metric refers to the percentage of time that the cpu used by user space'
        cpu_sys_percent_message='This metric refers to the percentage of time that the cpu used by system space'
        cpu_wait_percent_message='This metric refers to the percentage of time that the cpu is waiting for I/O'
        cpu_busy_percent_message='This metric refers to the percentage of time that the cpu is buzy i.e. not idle'
        cpu_idle_percent_message='This metric refers to the percentage of time that the cpu is idle, meaning that either it is waiting or doing nothing'

        if [ $(which sar) ]; then
                echo_debug "Gathering cpu metrics ... take few sec ..."
                #sar_cpu_avg_line=$(sar 1 $MAX_SAR_COUNT | awk '/^Average:/{print $0}')
                #sar_cpu_avg_load=$(sar -q 1 $MAX_SAR_COUNT | awk '/^Average:/{print $0}')
        else
                exit_error "unable to find 'sar' command - please check and install it the target server"
        fi

        if [ $(if sudo test -r /etc/cron.d/sysstat; then echo "ok"; else echo "ko"; fi) == "ok" ]; then
                sar_freq=$(sudo cat /etc/cron.d/sysstat | awk '!/^#/&&/sa1/{split($1,a,"/");print a[2]}')
                if [[ ${sar_freq:=-1} -gt 0 && ${sar_freq:=-1} -le 10 ]]; then
                        echo_debug "found sar frequency into '/etc/cron.d/sysstat' file : sar_freq=$sar_freq"
                else
                        exit_error "unable to find sar frequency into '/etc/cron.d/sysstat' file - please check configuration of the target server"
                fi
        else
                exit_error "unable to find '/etc/cron.d/sysstat' file - please check configuration of the target server"
        fi

        if [[ $ostype == "rhel" && $osver_major -ge 6 ]]; then
                SARFILE=/var/log/sa/sa$(date '+%d')
                sar_cpu_avg_line=$(sar -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        elif [[ $ostype == "debian" && $osver_major -gt 7 ]]; then
                SARFILE=/var/log/sysstat/sa$(date '+%d')
                sar_cpu_avg_line=$(sar -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        elif [[ $ostype == *sles* && $osver_major -ge 15 ]]; then
                SARFILE=/var/log/sa/sa$(date '+%Y%m%d')
                sar_cpu_avg_line=$(sar -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f $SARFILE -s $(date '+%H:%M:%S' --date '-20min') | awk '/^Average:/{print $0}')
        else
                exit_error "unable to find sar file for today in /var/log/sa/sa* or /var/log/sysstat/sa* - please check configuration of the target server"
        fi

        cpu_user_percent=$(echo $sar_cpu_avg_line | awk '/^Average:/{print $3}' | cut -d'.' -f1 )
        cpu_sys_percent=$(echo $sar_cpu_avg_line | awk '/^Average:/{print $5}' | cut -d'.' -f1 )
        cpu_wait_percent=$(echo $sar_cpu_avg_line | awk '/^Average:/{print $6}' | cut -d'.' -f1 )
        cpu_idle_percent=$(echo $sar_cpu_avg_line | awk '/^Average:/{print $8}' | cut -d'.' -f1 )
        cpu_busy_percent=$((100-cpu_idle_percent))

        # Gather CPU-queue related metrics

        cpu_nb_message='This metric refers to the number of configured cpu'
        cpu_runq_message='This metric refers to the cpu rune-queue, which means the number of process currently waiting for a cpu'
        cpu_runq_percent_message="This metric is a computed value showing the percentage of waiting process in the run-queue compared to the nb (cpu_nb=$cpu_nb) of available cpu = cpu_runq/cpu_nb*100 => cpu_runq_percent<100 means that not all cpu are used and no process are waiting, cpu_runq_percent=100 means that all cpu are used and no process are waiting, cpu_runq_percent>100 means that all cpu are busy and process are waiting for cpu"

        cpu_nb=$(cat /proc/cpuinfo | grep processor | wc -l)
        cpu_runq=$(echo $sar_cpu_avg_load | awk '/^Average:/{print $2}' )
        cpu_runq_percent=$((100*cpu_runq/cpu_nb))

        # Gather CPU-load-average related metrics

        cpu_loadavg1_message="This metric is a representing the system load average for the 1 minute.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg1_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 1 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"
        cpu_loadavg5_message="This metric is a representing the system load average for the 5 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval.It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg5_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 5 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"
        cpu_loadavg15_message="This metric is a representing the system load average for the 15 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg15_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 15 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"

        cpu_loadavg1=$(echo $sar_cpu_avg_load | awk '/^Average:/{print $4}' | cut -d'.' -f1 )
        cpu_loadavg5=$(echo $sar_cpu_avg_load | awk '/^Average:/{print $5}' | cut -d'.' -f1 )
        cpu_loadavg15=$(echo $sar_cpu_avg_load | awk '/^Average:/{print $6}' | cut -d'.' -f1 )

        cpu_loadavg1_canon_percent=$((100*cpu_loadavg1/cpu_nb))
        cpu_loadavg5_canon_percent=$((100*cpu_loadavg5/cpu_nb))
        cpu_loadavg15_canon_percent=$((100*cpu_loadavg15/cpu_nb))

        check_metric_not_empty "$LIST_METRICS_CPU"
}

#================= METRIC FUNCTION END

#================= HELPER FUNCTION BEGIN
usage(){
        echo "#Script usage is : $0 [-d] -m <monitor> [<monitor_param>]'"
        echo '#                : <monitor> must be always the last parameter'
        echo '#  >>>> from Solarwinds the component monitor script must be called by the following command line:'
        echo '#  >>>>         bash ${SCRIPT} -m <monitor>'
        echo -e "#Available monitors are:\n$(typeset -F | awk '/checkmon_/{print $NF}')"
        exit 1
}

echo_debug(){
        [ $DEBUG -eq 1 ] && echo -e "$1" | awk '{print "#DEBUG:"$0}'
}

exit_error(){
        error_message=$1
        error_code=$2
        echo_debug "#EXIT ERROR with error_code=$error_code - error_message=$error_message"
        exit  ${error_code:=1}
}

exit_ok(){
        echo_debug "#EXIT SUCCESS with error_code=0"
        exit 0
}

get_os(){
        if [ -f /etc/redhat-release ]; then
                ostype=$(awk '/^Red Hat Enterprise Linux/{print "rhel"}' /etc/redhat-release)
                osver=$(awk '/^Red Hat Enterprise Linux/{print $(NF-1)}' /etc/redhat-release)
                osver_major=$(awk '/^Red Hat Enterprise Linux/{print $(NF-1)}' /etc/redhat-release | cut -d'.' -f1)
        elif [ -f /etc/os-release ]; then
                ostype=$(awk -F'=' '/^ID/{print $2}' /etc/os-release)
                #ostype=$(awk -F'=' '/^ID/{print $2; exit}' /etc/os-release)
                osver=$(awk -F'=' '/^VERSION_ID/{gsub(/"/,"");print $2}' /etc/os-release)
                osver_major=$(awk -F'=' '/^VERSION_ID/{gsub(/"/,"");print $2}' /etc/os-release | cut -d'.' -f1 )
        else
                exit_error "#cannot find ostype : $(uname -a)"
        fi

        if [ $(sudo dmidecode -s system-product-name | grep -c "VMware Virtual Platform") -eq 1 ]; then
                machine_type="virtual"
        else
                machine_type="physical"
        fi

        echo_debug "ostype=$ostype"
        echo_debug "osver=$osver"
        echo_debug "osver_major=$osver_major"
        echo_debug "machine_type=$machine_type"
}

check_metric_not_empty(){
        LIST=$1
        error_msg=""

        for metric in $(echo $LIST | sed  's/,/ /g'); do
                value="$(eval echo \$$metric)"
                echo_debug "metric=$metric - value=$value"
                if [ "$value" == "" ]; then
                        error_msg+="ERROR unknow metric $metric\n"
                fi
        done

        echo_debug "$error_msg"

        if [ "$error_msg" != "" ]; then
                exit_error "$error_msg"
        fi
}

print_stat(){
        LIST=$1

        echo_debug "LIST=$LIST"

        i=1
        for metric in $(echo $LIST | sed  's/,/ /g'); do
                value="$(eval echo \$${metric})"
                if [[ "$WARN_def" == '' || "$CRIT_def" == '' ]]; then
                        threshold_message=""
                else
                        threshold_message="[ALERT WARN_def=$WARN_def - CRIT_def=$CRIT_def]"
                fi
                message="$(eval echo \$${metric}_message)"
                echo_debug "#########################\n"
                echo_debug "#####  metric=$metric - value=$value - message=$message - threshold_message=$threshold_message"
                echo "Statistic.$metric:$value"
                echo "Message.$metric:#${i} [ $metric = $value ] $message $threshold_message"
                i=$((i+1))
        done
}

#================= HELPER FUNCTION END

#================= MAIN BEGIN

#define variables
DEBUG=0
OK_alert=0
WARN_alert=2
CRIT_alert=3
WARN_def=''
CRIT_def=''
MAX_SAR_COUNT=5                                         #number of SAR count on which the average value is computed
NOT_MONITORED_SVC=/etc/LDC/not_monitored_service         #list all the service which should be exclued from the monitoring list : one service name per line
MONITORED_SVC=/etc/LDC/monitored_service                #list all the service which should be INCLUDED from the monitoring list : one service name per line

#parse option
options=':dm:'
while getopts $options option
do
    case "$option" in
        d  ) DEBUG=1;echo_debug "#Debug mode";;
        m  ) monitor=$OPTARG  ;;
        \? ) echo "#Unknown option: -$OPTARG" >&2; usage;;
        :  ) echo "#Missing option argument for -$OPTARG" >&2; usage;;
        *  ) echo "#Not existing option: -$OPTARG" >&2; usage;;
    esac
done
shift $((OPTIND - 1))
if [ "$(typeset -F | awk '$NF ~ /^'"${monitor:="#"}"'$/{print $0}')" == "" ]; then usage; fi

echo_debug "#Check monitor=$monitor"
get_os
$monitor $1
#================= MAIN END

