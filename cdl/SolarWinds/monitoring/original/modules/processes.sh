# shellcheck disable=SC2034
# shellcheck disable=SC2031

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

        zombie_proc_message='That metric refers to the number of zombie process currently running on the system.'

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

        max_inode_percent=$(echo "$max_inode" | cut -d'|' -f1 | cut -d'.' -f1)
        max_inode_fs=$(echo "$max_inode" | cut -d'|' -f2)

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

#        if [ -f $MONITORED_SVC ]; then
#                echo_debug "checking INCLUDE list MONITORED_SVC=$MONITORED_SVC\n$(cat $MONITORED_SVC)"
#                for service in $(cat $MONITORED_SVC); do
#                        echo_debug "Adding service=$service in monitored list as listed in MONITORED_SVC=$MONITORED_SVC"
#                        SERVICE_SYSTEM_LIST="$SERVICE_SYSTEM_LIST $service"
#                done
#        fi

        if [ -f $MONITORED_SVC ]; then
                echo_debug "checking INCLUDE list MONITORED_SVC=$MONITORED_SVC\n$(cat $MONITORED_SVC)"
                while read -r line; do
                  echo_debug "Adding service=$line in monitored list as listed in MONITORED_SVC=$MONITORED_SVC"
                  SERVICE_SYSTEM_LIST="$SERVICE_SYSTEM_LIST $line"
                done <$MONITORED_SVC
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
                if [[ -f $NOT_MONITORED_SVC && $(grep -e "^${service_name}$" -c $NOT_MONITORED_SVC) -ne 0 ]]; then
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
                                service_status=$(sudo systemctl status "$service_name" 2>&1 |
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
                                service_status=$(sudo /etc/init.d/"${service_name}" status 2>&1 |
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
                                        service_status=$(sudo /etc/"${service_name}"/services.sh status 2>&1 |
                                                awk -v ok=$OK_alert -v warn=$WARN_alert -v crit=$CRIT_alert '
                                                BEGIN{alert_status=crit}
                                                /running/{alert_status=ok}
                                                END{print alert_status}'
                                        )
                                elif [[ -f /etc/rc.d/init.d/${service_name} ]]; then
                                        #check if service should be running at runlevel=3
                                        service_name_enable=$(chkconfig --list "$service_name" | awk '{split($5,e,":");print e[2]}')
                                        if [  "$service_name_enable" == "on" ]; then
                                                service_status=$(sudo service "$service_name" status 1>/dev/null 2>&1;echo $? |
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
                                service_status=$(sudo systemctl status "$service_name" 2>&1 |
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
                        if [ "${service_tab[$key]}" -ge "$max_value" ]; then
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



#================= HELPER FUNCTION BEGIN
usage(){
        echo "#Script usage is : $0 [-d] -m <monitor> [<monitor_param>]'"
        echo "#                : <monitor> must be always the last parameter"
        echo "#  >>>> from Solarwinds the component monitor script must be called by the following command line:"
        echo "#  >>>>         bash ${SCRIPT} -m <monitor>"
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
        exit  "${error_code:=1}"
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

        for metric in $(echo "$LIST" | sed  's/,/ /g'); do
                value="$(eval echo \$"$metric")"
                echo_debug "metric=$metric - value=$value"
                if [ "$value" == "" ]; then
                        error_msg+="ERROR unknown metric $metric\n"
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
        for metric in $(echo "$LIST" | sed  's/,/ /g'); do
                value="$(eval echo \$"${metric}")"
                if [[ "$WARN_def" == '' || "$CRIT_def" == '' ]]; then
                        threshold_message=""
                else
                        threshold_message="[ALERT WARN_def=$WARN_def - CRIT_def=$CRIT_def]"
                fi
                message="$(eval echo \$"${metric}"_message)"
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
NOT_MONITORED_SVC=/etc/LDC/not_monitored_service         #list all the service which should be excluded from the monitoring list : one service name per line
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
