#!/bin/bash
##############################################################################################
# AWX Config-as-Code Core Script

# usage: launch_awx_caac_core.sh -e <env> [-- <extra ansible params>]

while getopts "e:" option; do
  case $option in
    e)
      echo "# ==> environment env=${OPTARG} selected"
      export env=${OPTARG}
    ;;
  esac
  # future logic here if needed
done

shift $((OPTIND-1))
PARAM=$*

timestamp="$(date '+%Y%m%d-%H%M%S')"
LOGDIR="./logs"
mkdir -p "$LOGDIR"


# main playbook and inventory (adjust as needed)
PLAYBOOK="./controller_config.yml"
INVENTORY="inventory_${env}.yml"

# Use ansible-playbook directly (skip execution environments for AWX on VM)
if command -v ansible-playbook &> /dev/null; then
    echo "# Using ansible-playbook (native AWX environment)"

    cmd="ansible-playbook $PLAYBOOK $PARAM -i $INVENTORY --ask-vault-pass"
    echo "# Execute cmd=$cmd"
    time eval $cmd | tee "${LOGDIR}/AWX_controller_config_${env}_${timestamp}.log"
else
    echo "# ERROR: ansible-playbook not found!"
    echo "# Install with: pipx install ansible-core"
    echo "# Then install collections: ansible-galaxy collection install -r requirements.yml"
    exit 1
fi

echo ""
echo "#Check log file ${LOGDIR}/AWX_controller_config_${env}_${timestamp}.log"
##############################################################################################
