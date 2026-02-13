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
  echo "# AAP EEI image check published on EE nodes"
  echo "#"
  echo "# Syntax: $0 -e [prod|valid]"
  echo "#     -e [prod|valid] : select environment"
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
while getopts "e:" option; do
  case $option in
    e)
      export env=${OPTARG}
      echo "# ==> environment selected => env=${env} "
      if [ $(echo $env | egrep -c '^(prod|valid)$') -ne 0 ]; then
        case $env in
          'prod')
            ee_server_list="csm1patwexe001 csm1patwexe002"
            aaphub='csm1patwhub001.d1.ad.local'
          ;;
          'valid')
            ee_server_list="csm1vatwexe001"
            aaphub='csm1vatwhub001.d1.ad.local'
          ;;
        esac
      else
        echo "# ==> WRONG environment selected => env=${env}"
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

echo "# Run command : $0 -e $env -- $PARAM"

logfile="/data/logs/.$(basename $0 .sh)logs.$(date '+%Y%m%d-%H%M%S')"

exec &> >(tee -a "$logfile")

#echo " #Define image paramters"
#source ./config_aaphub_eei_image_param

# ====================================================

eei_image_history="eei_image_history_${env}"
eei_deployed_image="eei_image_history_${env}_deployed"
eei_deployed_image_history="eei_image_history_folder_deployed/${eei_deployed_image}.$(date '+%Y%m%d-%H%M%S')"

podman_cmd="podman images -n --format \\\"{{.Repository}}|{{.CreatedTime}}|{{.ID}}|{{.Tag}}\\\" --sort created | sort -b -t'|' -k2"

#cd /data/ATW-AAP-configuration/ee_manual

aapuser="atwaap${env}"
rsa_key=~/.ssh/id_rsa_${env}


for ee_server in $ee_server_list; do
        echo "#EEI DEPLOYED IMAGES HISTORY" > ${eei_deployed_image_history}.tmp
        echo "#=== ee_server=$ee_server at $(date)"
        ssh -q -i $rsa_key ${aapuser}@$ee_server "sudo su - awx -c \"$podman_cmd\"" | awk -v server=$ee_server '{print server"|"$0}' >> ${eei_deployed_image_history}.tmp

                for image in $(awk -F'|' '$2 ~ /^'"${aaphub}"':443/{print $2}' ${eei_deployed_image_history}.tmp | sort -u); do
                        unset ee_ver_prod_hash ee_ver_dev_hash ee_ver_test_hash ee_ver_poc_hash ee_ver_prod ee_ver_dev ee_ver_test ee_ver_poc
                        imagen=$(echo $image | sed 's/\//\\\//g')

                        #echo "image=$image - imagen=$imagen"

                        ee_ver_prod_hash=$(awk -F'|' '$2 ~ /^'$imagen'$/{print $0}' ${eei_deployed_image_history}.tmp | awk -F'|' 'BEGIN{hash="000000000000"}$NF~/(^| )prod( |$)/{hash=$4}END{print hash}')
                        ee_ver_dev_hash=$(awk -F'|' '$2 ~ /^'$imagen'$/{print $0}' ${eei_deployed_image_history}.tmp | awk -F'|' 'BEGIN{hash="000000000000"}$NF~/(^| )dev( |$)/{hash=$4}END{print hash}')
                        ee_ver_test_hash=$(awk -F'|' '$2 ~ /^'$imagen'$/{print $0}' ${eei_deployed_image_history}.tmp | awk -F'|' 'BEGIN{hash="000000000000"}$NF~/(^| )test( |$)/{hash=$4}END{print hash}')
                        ee_ver_poc_hash=$(awk -F'|' '$2 ~ /^'$imagen'$/{print $0}' ${eei_deployed_image_history}.tmp | awk -F'|' 'BEGIN{hash="000000000000"}$NF~/(^| )poc( |$)/{hash=$4}END{print hash}')

                        ee_ver_prod=$(awk -F'|' '/'"$ee_ver_prod_hash"'/{print $4}' $eei_image_history | awk 'BEGIN{ver="unknown"}{ver=$1}END{print ver}')
                        ee_ver_dev=$(awk -F'|' '/'"$ee_ver_dev_hash"'/{print $4}' $eei_image_history | awk 'BEGIN{ver="unknown"}{ver=$1}END{print ver}')
                        ee_ver_test=$(awk -F'|' '/'"$ee_ver_test_hash"'/{print $4}' $eei_image_history | awk 'BEGIN{ver="unknown"}{ver=$1}END{print ver}')
                        ee_ver_poc=$(awk -F'|' '/'"$ee_ver_poc_hash"'/{print $4}' $eei_image_history | awk 'BEGIN{ver="unknown"}{ver=$1}END{print ver}')

                        #echo "ee_ver_prod_hash=$ee_ver_prod_hash - ee_ver_prod=$ee_ver_prod"
                        #echo "ee_ver_dev_hash=$ee_ver_dev_hash - ee_ver_dev=$ee_ver_dev"
                        #echo "ee_ver_test_hash=$ee_ver_test_hash - ee_ver_test=$ee_ver_test"
                        #echo "ee_ver_poc_hash=$ee_ver_poc_hash - ee_ver_poc=$ee_ver_poc"

                        awk -F'|' '$2 ~ /^'$imagen'$/{print $0}' ${eei_deployed_image_history}.tmp | awk -F'|' '
                                                        BEGIN{print_ok=1}
                                                        $5 ~ /^poc$/ && $4 ~ /'"$ee_ver_poc_hash"'/{print $0"|'"$ee_ver_poc"'|ok";print_ok=0}
                                                        $5 ~ /^test$/ && $4 ~ /'"$ee_ver_test_hash"'/{print $0"|'"$ee_ver_test"'|ok";print_ok=0}
                                                        $5 ~ /^dev$/ && $4 ~ /'"$ee_ver_dev_hash"'/{print $0"|'"$ee_ver_dev"'|ok";print_ok=0}
                                                        $5 ~ /^prod$/ && $4 ~ /'"$ee_ver_prod_hash"'/{print $0"|'"$ee_ver_prod"'|ok";print_ok=0}
                                                        print_ok ==1{print "#"$0}
                                                        {print_ok=1}
                                                        ' >> ${eei_deployed_image_history}

                done
                rm ${eei_deployed_image_history}.tmp
done


#=> Display image history
echo "#Updated image deployement history for eei_deployed_image_history:${eei_deployed_image_history}"
cat $eei_deployed_image_history

ln -fs $eei_deployed_image_history ${eei_deployed_image}

ls -al ${eei_deployed_image}*

############################
