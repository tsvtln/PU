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



get_mem_use(){
        # Function to gather both memory and swap usage

        LIST_METRICS_MEM="mem_total,mem_used,mem_avail,mem_avail_percent,swap_total,swap_used,swap_used_percent,swap_mem_percent,swap_opt_size,swap_size_ok,MEM_LOWWATERMARK,COMPUTED_MEMINFO_MEMAVAILABLE,MEMAVAILABLERESERVED,MEMAVAILABLERESERVED_PERCENT"

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
        mem_avail_message='This metric refers to the available memory in Kb (for RHEL6 it is the sum of free+cache-min_free / for RHEL7+ and Debian, it refers to availaible mem which is the estimated amount of memory usabled by new application after releasing eventually some memory pages used for cache)'
        mem_avail_percent_message="This metric is a computed value showing the percentage of available memory = mem_avail/mem_total*100 ([mem_avail=$mem_avail]:$mem_avail_message) ([mem_total=$mem_total]:$mem_total_message)"

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
