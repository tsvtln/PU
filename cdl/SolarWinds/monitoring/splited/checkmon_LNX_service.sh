#!/bin/bash

: <<'END_COMMENT'
this metric refers to the status of system services.
0 = ok
3 = nok

usage:
check_service_status.sh         # uses default service list
check_service_status.sh sshd    # checks only 'sshd'

respects /etc/LDC/monitored_service and /etc/LDC/not_monitored_service
supports rhel, debian, sles, legacy init scripts, and systemctl
designed to mirror the original logic but run standalone
END_COMMENT

# configurable paths (adjust if needed)
NOT_MONITORED_SVC=/etc/LDC/not_monitored_service
MONITORED_SVC=/etc/LDC/monitored_service

OK_alert=0
CRIT_alert=3

DEBUG=0
echo_debug() {
    [ "$DEBUG" -eq 1 ] && echo "#debug: $*"
}

# detect os flavour
get_os() {
    if [ -f /etc/redhat-release ]; then
        ostype="rhel"
        osver=$(awk '{print $(NF-1)}' /etc/redhat-release)
        osver_major=$(echo "$osver" | cut -d'.' -f1)
    elif [ -f /etc/os-release ]; then
        ostype=$(awk -F'=' '/^ID=/{gsub(/"/,""); print $2}' /etc/os-release)
        osver=$(awk -F'=' '/^VERSION_ID=/{gsub(/"/,""); print $2}' /etc/os-release)
        osver_major=$(echo "$osver" | cut -d'.' -f1)
    else
        echo "Statistic.service_status:3"
        echo "Message.service_status: ERROR: Cannot detect os version"
        exit 1
    fi
}

check_service_status() {
    get_os
    service_arg="$1"
    service_list=""

    # list of services specific per os flavour
    SERVICE_SYSTEM_LIST_RHEL7="auditd chronyd crond sshd firewalld rsyslog systemd-logind systemd-journald"
    SERVICE_SYSTEM_LIST_RHEL8="auditd chronyd crond sshd firewalld rsyslog systemd-logind systemd-journald"
    SERVICE_SYSTEM_LIST_RHEL9="auditd chronyd crond sshd firewalld rsyslog systemd-logind systemd-journald"
    SERVICE_SYSTEM_LIST_DEBIAN10="cron ssh rsyslog"
    SERVICE_SYSTEM_LIST_DEBIAN11="cron ssh rsyslog"
    SERVICE_SYSTEM_LIST_DEBIAN12="cron ssh rsyslog"
    SERVICE_SYSTEM_LIST_SLES15="auditd chronyd cron sshd rsyslog wicked firewalld"
    SERVICE_SYSTEM_LIST_UBUNTU="cron ssh rsyslog systemd-journald systemd-logind"

    # os case block
    if [[ $ostype == "rhel" && $osver_major -eq 7 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_RHEL7"
    elif [[ $ostype == "rhel" && $osver_major -eq 8 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_RHEL8"
    elif [[ $ostype == "rhel" && $osver_major -eq 9 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_RHEL9"
    elif [[ $ostype == "debian" && $osver_major -eq 10 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_DEBIAN10"
    elif [[ $ostype == "debian" && $osver_major -eq 11 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_DEBIAN11"
    elif [[ $ostype == "debian" && $osver_major -eq 12 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_DEBIAN12"
    elif [[ $ostype == "ubuntu" ]]; then
        service_list="$SERVICE_SYSTEM_LIST_UBUNTU"
    elif [[ $ostype == *sles* && $osver_major -eq 15 ]]; then
        service_list="$SERVICE_SYSTEM_LIST_SLES15"
    fi

    # add the services from the monitored config
    if [[ -f "$MONITORED_SVC" ]]; then
        service_list+=" $(cat "$MONITORED_SVC")"
    fi

    # check for user input
    if [[ -n "$service_arg" && "$service_arg" != "default" ]]; then
        service_list="$service_arg"
    fi

    max_value=0
    max_key=""
    sum_value=0

    for service_name in $service_list; do
        # skip not-monitored list
        if [[ -f "$NOT_MONITORED_SVC" && $(grep -c "^$service_name$" "$NOT_MONITORED_SVC") -ne 0 ]]; then
            echo_debug "Skipping $service_name (excluded)"
            continue
        fi

        # assume critical by default (service not found)
        service_status=$CRIT_alert

        if command -v systemctl >/dev/null; then
          if systemctl status "$service_name" &>/dev/null; then
              active_status=$(systemctl is-active "$service_name" 2>/dev/null)
              if [[ "$active_status" == "active" ]]; then
                  service_status=$OK_alert
              else
                  service_status=$CRIT_alert
              fi
          else
              echo_debug "Service '$service_name' not found or not manageable by systemctl – assuming critical"
          fi

        elif [[ -x /etc/init.d/$service_name ]]; then
            /etc/init.d/"$service_name" status >/dev/null 2>&1
            if [[ $? -eq 0 ]]; then
                service_status=$OK_alert
            else
                service_status=$CRIT_alert
            fi
        else
            echo_debug "No supported service manager found for $service_name"
        fi

        if (( service_status > max_value )); then
            max_value=$service_status
            max_key="$service_name"
        fi

        sum_value=$((sum_value + service_status))
    done

    if (( sum_value > 0 )); then
        caption="Service '$max_key' has a not ok status"
    else
        caption="All checked services have ok status"
    fi

    service_status_message="$caption among: [$service_list]. Service Status Code = $OK_alert → OK, $CRIT_alert → NOK."
    echo "Statistic.service_status:$max_value"
    echo "Message.service_status:$service_status_message"
    return "$max_value"
}

check_service_status "$1"
