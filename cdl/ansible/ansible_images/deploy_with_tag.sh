#!/bin/bash
##############################################################################################

#==================
# usage function
usage(){
  echo ""
  echo "###################################"
  echo "#"
  echo "# Usage for $0 launched with args $*"
  echo "#"
  echo "# AAP EEI image deply on EE nodes by tag"
  echo "#"
  echo "# Syntax: $0 -e [prod|valid] -t [prod|dev|test|poc]"
  echo "#     -e [prod|valid] : select environment"
  echo "#     -t [prod|dev|test|poc] : select tag"
  echo "#"
  echo "###################################"
  exit 1
}

#==================
# Get input
if [ -z "$*" ]; then
  echo "Arguments are mandatory"
  usage
fi
while getopts "e:t:" option; do
  case $option in
    e)
      export env=${OPTARG}
      echo "# ==> environment selected => env=${env} "
      if [ $(echo $env | egrep -c '^(prod|valid)$') -ne 0 ]; then
        case $env in
          'prod')
            ee_server_list="csm1patwexe001 csm1patwexe002"
            aaphub='csm1patwhub001.d1.ad.local'
            #AUTHFILE="config_auth.json"
          ;;
          'valid')
            ee_server_list="csm1vatwexe001"
            aaphub='csm1vatwhub001.d1.ad.local'
            #AUTHFILE="config_auth-val.json"
          ;;
        esac
      else
        echo "# ==> WRONG environment selected => env=${env}"
        usage
      fi
    ;;
    t)
      export tag=${OPTARG}
      echo "# ==> tag selected => tag=${tag}"
      if [ $(echo $tag | egrep -c '^(prod|dev|test|poc)$') -eq 0 ]; then
        echo "# ==> WRONG tag selected => tag=${OPTARG}"
        usage
      fi
    ;;
    *)
      usage
    ;;
        esac
done

shift $((OPTIND-1))
PARAM=$*

echo "# Run command : $0 -e $env -t $tag -- $PARAM"

logfile="/data/logs/.$(basename $0 .sh)logs.$(date '+%Y%m%d-%H%M%S')"

exec &> >(tee -a "$logfile")

#echo " #Define image paramters"
#source ./config_aaphub_eei_image_param
AUTHFILE="config_aaphub_${env}/config_aaphub_auth.json"

echo "Check deployed eeir on exec env $ee_server_list"
./${env}_03_ansible_eei_check_deployed_on_ee_node.sh

unset eei_image_not_deployed_hash
declare -A eei_image_not_deployed_hash

unset eei_image_name eei_image_version exists_remote_image found_remote_image eei_image_to_publish server
# Use a for loop to process each line
IFS_bkp=$IFS
IFS=$'\n' # Set the Internal Field Separator to newline
image_index=0
nb_exec_env=$(echo $ee_server_list | wc -w)
for line in $(podman images -n --sort created | grep $aaphub | grep -v 'ansible-automation-platform' | grep $tag); do
  unset found_deployed_image
  #echo "#==============="
  eei_image_name=$(echo $line | awk '{print $1}')
  eei_image_version=$(echo $line | awk '{print $2}')
  eei_image_id=$(echo $line | awk '{print $3}')
  #echo "serach eei_image_name=$eei_image_name - eei_image_version=$eei_image_version - eei_image_id=$eei_image_id"
  found_remote_image=$(podman search --list-tags ${eei_image_name} | awk '$2~/^'"${eei_image_version}"'$/{print $0}')
  #echo "found_remote_image=$found_remote_image"
  exists_remote_image=0
  if [ -n "$found_remote_image" ]; then
        exists_remote_image=1
                total_found_deployed_image=0
                #echo "total_found_deployed_image=$total_found_deployed_image"
                IFS=$IFS_bkp
                for server in $ee_server_list; do
                        #echo "server=$server"
                        #egrep '^'$server'.*ok$' eei_image_history_prod_deployed
                        #egrep '^'$server'.*ok$' eei_image_history_prod_deployed | grep -c $eei_image_id
                        found_deployed_image=$(egrep '^'$server'.*ok$' eei_image_history_prod_deployed | grep $tag | grep -c $eei_image_id)
                        found_deployed_image_version=$(egrep '^'$server'.*ok$' eei_image_history_prod_deployed | grep $tag | grep $eei_image_id | awk -F'|' '{print $5"-"$6}')
                        total_found_deployed_image=$(($total_found_deployed_image + $found_deployed_image))
                done
                #echo "total_found_deployed_image=$total_found_deployed_image"
                if [[ $total_found_deployed_image -eq $nb_exec_env ]]; then
                        total_found_deployed_image="[$found_deployed_image_version] ${total_found_deployed_image}-fully_deployed"
                elif [[ $total_found_deployed_image -lt $nb_exec_env && $total_found_deployed_image -gt 0 ]]; then
                        total_found_deployed_image="[$found_deployed_image_version] ${total_found_deployed_image}-partially_deployed"
                elif [[ $total_found_deployed_image -le 0 ]]; then
                        total_found_deployed_image="[$found_deployed_image_version] ${total_found_deployed_image}-not_deployed"
                else
                        total_found_deployed_image="[$found_deployed_image_version] ${total_found_deployed_image}-unknown"
                fi
        eei_image_not_deployed_hash[$image_index]="${eei_image_name}:${eei_image_version}|[$eei_image_id]|$total_found_deployed_image"
        image_index=$(($image_index+1))
  fi
  #echo "eei_image_name=$eei_image_name - eei_image_version=$eei_image_version => exists_remote_image=$exists_remote_image"
  #echo "#==============="
done
unset eei_image_name eei_image_version exists_remote_image found_remote_image
IFS=$IFS_bkp

# Print the array to verify
echo "#Please select the image to publish to tag=$tag"
for key in "${!eei_image_not_deployed_hash[@]}"; do
    echo -e "[$key] = ${eei_image_not_deployed_hash[$key]}"
done | column -t -s '|'

# Prompt for eei_index with a default value of 0
eei_index_default=0
read -p "Enter an eei_index (default is 0): " eei_index
eei_index=${eei_index:-$eei_index_default}

# Check if the entered index is valid
if [[ -v eei_image_not_deployed_hash[$eei_index] ]]; then
    echo "You selected: eei_image_not_deployed_hash[$eei_index]=${eei_image_not_deployed_hash[$eei_index]}"
    eei_image_to_publish=${eei_image_not_deployed_hash[$eei_index]}
    eei_image_name=$(echo $eei_image_to_publish | awk -F'[/:|]' '{print $2}')
    eei_image_version=$(echo $eei_image_to_publish | awk -F'[/:|]' '{print $3}')
    #echo "eei_image_to_publish=$eei_image_to_publish"
    echo "eei_image_name=$eei_image_name - eei_image_version=$eei_image_version"
else
    echo "Invalid index. Please enter a valid index. eei_image_not_deployed_hash[$eei_index] does not exists"
    exit 1
fi

# ====================================================

podman_cmd="podman pull --authfile=config_aaphub_auth.json ${aaphub}:443/${eei_image_name}:${tag} ${aaphub}/${eei_image_name}:${tag}"

#cd /data/ATW-AAP-configuration/ee_manual

aapuser="atwaap${env}"
rsa_key=~/.ssh/id_rsa_${env}

# Check if AUTHFILE exists
if [ ! -f "$AUTHFILE" ]; then
  echo "ERROR: Auth file not found: $AUTHFILE"
  exit 1
fi

for ee_server in $ee_server_list; do
  echo "#=== ee_server=$ee_server at $(date)"
  echo "# Execute command podman_cmd=\"$podman_cmd\""

  # Test SSH connection first
  if ! ssh -i $rsa_key -o ConnectTimeout=5 ${aapuser}@$ee_server "echo 'SSH OK'" 2>&1 | grep -q "SSH OK"; then
    echo "ERROR: Cannot connect to $ee_server"
    continue
  fi

  # Copy auth file
  if ! scp -i $rsa_key $AUTHFILE ${aapuser}@$ee_server:config_aaphub_auth.json; then
    echo "ERROR: SCP failed for $ee_server"
    continue
  fi

  # Execute commands step by step with better error handling
  ssh -i $rsa_key ${aapuser}@$ee_server << ENDSSH
sudo cp config_aaphub_auth.json /var/lib/awx/config_aaphub_auth.json
sudo chown awx:awx /var/lib/awx/config_aaphub_auth.json
sudo chmod 600 /var/lib/awx/config_aaphub_auth.json
sudo su - awx -c "podman pull --authfile=/var/lib/awx/config_aaphub_auth.json ${aaphub}:443/${eei_image_name}:${tag}"
sudo su - awx -c "podman tag ${aaphub}:443/${eei_image_name}:${tag} ${aaphub}/${eei_image_name}:${tag}"
ENDSSH

  if [ $? -ne 0 ]; then
    echo "ERROR: Podman pull failed on $ee_server"
  else
    echo "SUCCESS: Image deployed on $ee_server"
  fi
done

./${env}_03_ansible_eei_check_deployed_on_ee_node.sh

############################