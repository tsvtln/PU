# shellcheck disable=SC2034

checkmon_LNX_cpu_ALL(){
        # Display multiple statistics related to CPU metrics
        get_cpu_use

        print_stat "$LIST_METRICS_CPU"
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




get_cpu_use(){
        # Function to check CPU usage and CPU run queue

        LIST_METRICS_CPU="cpu_user_percent,cpu_sys_percent,cpu_wait_percent,cpu_busy_percent,cpu_idle_percent,cpu_runq,cpu_runq_percent,cpu_loadavg1,cpu_loadavg5,cpu_loadavg15"

        # Gather CPU related metrics

        cpu_user_percent_message='This metric refers to the percentage of time that the cpu used by user space'
        cpu_sys_percent_message='This metric refers to the percentage of time that the cpu used by system space'
        cpu_wait_percent_message='This metric refers to the percentage of time that the cpu is waiting for I/O'
        cpu_busy_percent_message='This metric refers to the percentage of time that the cpu is buzy i.e. not idle'
        cpu_idle_percent_message='This metric refers to the percentage of time that the cpu is idle, meaning that either it is waiting or doing nothing'

        if [ "$(which sar)" ]; then
                echo_debug "Gathering cpu metrics ... take few sec ..."
                #sar_cpu_avg_line=$(sar 1 $MAX_SAR_COUNT | awk '/^Average:/{print $0}')
                #sar_cpu_avg_load=$(sar -q 1 $MAX_SAR_COUNT | awk '/^Average:/{print $0}')
        else
                exit_error "unable to find 'sar' command - please check and install it on the target server"
        fi

        if [ "$(if sudo test -r /etc/cron.d/sysstat; then echo "ok"; else echo "ko"; fi)" == "ok" ]; then
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
                sar_cpu_avg_line=$(sar -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        elif [[ $ostype == "debian" && $osver_major -gt 7 ]]; then
                SARFILE=/var/log/sysstat/sa$(date '+%d')
                sar_cpu_avg_line=$(sar -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        elif [[ $ostype == *sles* && $osver_major -ge 15 ]]; then
                SARFILE=/var/log/sa/sa$(date '+%Y%m%d')
                sar_cpu_avg_line=$(sar -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        sar_cpu_avg_load=$(sar -q -f "$SARFILE" -s "$(date '+%H:%M:%S' --date '-20min')" | awk '/^Average:/{print $0}')
        else
                exit_error "Unable to find sar file for today in /var/log/sa/sa* or /var/log/sysstat/sa* -
                please check configuration of the target server"
        fi

        cpu_user_percent=$(echo "$sar_cpu_avg_line" | awk '/^Average:/{print $3}' | cut -d'.' -f1 )
        cpu_sys_percent=$(echo "$sar_cpu_avg_line" | awk '/^Average:/{print $5}' | cut -d'.' -f1 )
        cpu_wait_percent=$(echo "$sar_cpu_avg_line" | awk '/^Average:/{print $6}' | cut -d'.' -f1 )
        cpu_idle_percent=$(echo "$sar_cpu_avg_line" | awk '/^Average:/{print $8}' | cut -d'.' -f1 )
        cpu_busy_percent=$((100-cpu_idle_percent))

        # Gather CPU-queue related metrics

        cpu_nb_message='This metric refers to the number of configured cpu'
        cpu_runq_message='This metric refers to the cpu rune-queue,
        which means the number of process currently waiting for a cpu'
        cpu_runq_percent_message="This metric is a computed value showing the percentage of waiting process in the run-queue compared to the nb (cpu_nb=$cpu_nb) of available cpu = cpu_runq/cpu_nb*100 => cpu_runq_percent<100 means that not all cpu are used and no process are waiting, cpu_runq_percent=100 means that all cpu are used and no process are waiting, cpu_runq_percent>100 means that all cpu are busy and process are waiting for cpu"

        # Returns incorrect number of cores.
        # cpu_nb=$(cat "/proc/cpuinfo" | grep -c processor | wc -l)

        cpu_nb=$(grep -c processor /proc/cpuinfo)
        cpu_runq=$(echo "$sar_cpu_avg_load" | awk '/^Average:/{print $2}' )
        cpu_runq_percent=$((100*cpu_runq/cpu_nb))

        # Gather CPU-load-average related metrics

        cpu_loadavg1_message="This metric is a representing the system load average for the 1 minute.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg1_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 1 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"
        cpu_loadavg5_message="This metric is a representing the system load average for the 5 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval.It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg5_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 5 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"
        cpu_loadavg15_message="This metric is a representing the system load average for the 15 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. It has to be analyzed compared of the current number of cpu cpu_nb=$cpu_nb"
        cpu_loadavg15_canon_percent_message="This metric is a representing the system canonical per-cpu based load average for the 15 minutes.  The load average is calculated as the average number of runnable or  running tasks (R state), and the number of tasks in uninterruptible sleep (D state) over the specified interval. The result is divised by the current number of cpu cpu_nb=$cpu_nb and givent in percentage"

        cpu_loadavg1=$(echo "$sar_cpu_avg_load" | awk '/^Average:/{print $4}' | cut -d'.' -f1 )
        cpu_loadavg5=$(echo "$sar_cpu_avg_load" | awk '/^Average:/{print $5}' | cut -d'.' -f1 )
        cpu_loadavg15=$(echo "$sar_cpu_avg_load" | awk '/^Average:/{print $6}' | cut -d'.' -f1 )

        cpu_loadavg1_canon_percent=$((100*cpu_loadavg1/cpu_nb))
        cpu_loadavg5_canon_percent=$((100*cpu_loadavg5/cpu_nb))
        cpu_loadavg15_canon_percent=$((100*cpu_loadavg15/cpu_nb))

        check_metric_not_empty "$LIST_METRICS_CPU"
}




#================= HELPER FUNCTION BEGIN
usage(){
        echo "#Script usage is : $0 [-d] -m <monitor> [<monitor_param>]"
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
