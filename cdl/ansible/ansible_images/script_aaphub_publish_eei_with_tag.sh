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
  echo "# AAP EEI image publish with tag"
  echo "#"
  echo "# Syntax: $0 -e [prod|valid] -t [prod|dev|test]"
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
            aaphub='csm1patwhub001.d1.ad.local'
            #AUTHFILE="config_auth.json"
          ;;
          'valid')
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

echo " #Define image paramters"
#source ./config_aaphub_eei_image_param
unset eei_image_hash
declare -A eei_image_hash

# Use a for loop to process each line
IFS_bkp=$IFS
IFS=$'\n' # Set the Internal Field Separator to newline
image_index=0
for eei_image_id in $(podman images -n --sort created | grep $aaphub | grep -v 'ansible-automation-platform' | awk '{print $3}' | uniq); do

  eei_image_info=$(podman images -n --sort created | awk 'BEGIN{ver=""}$3 ~ /^'"$eei_image_id"'$/{eei_name=$1;ver=sprintf("%s%s|",ver,$2)}END{gsub(/\|$/,"",ver);print eei_name"#"ver}')
  eei_image_name=$(echo $eei_image_info | awk -F'#' '{print $1}')
  eei_image_ver=$(echo $eei_image_info | awk -F'#' '{print $2}')

  #echo "eei_image_id=$eei_image_id - eei_image_info=$eei_image_info - eei_image_name=$eei_image_name - eei_image_ver=$eei_image_ver"

  eei_image_hash[$image_index]=${eei_image_name}:${eei_image_ver}
  image_index=$(($image_index+1))

done

# Print the array to verify
echo "#Please select the image to publish to tag=$tag"
for key in "${!eei_image_hash[@]}"; do
    echo "[$key] = ${eei_image_hash[$key]}"
done

# Prompt for eei_index with a default value of 0
eei_index_default=0
read -p "Enter an eei_index (default is 0): " eei_index
eei_index=${eei_index:-$eei_index_default}

# Check if the entered index is valid
if [[ -v eei_image_hash[$eei_index] ]]; then
    echo "You selected: eei_image_hash[$eei_index]=${eei_image_hash[$eei_index]}"
    eei_image_to_publish=${eei_image_hash[$eei_index]}
    eei_image_name=$(echo $eei_image_to_publish | awk -F'[/:]' '{print $2}')
    # Extract only the first tag before any pipe character
    eei_image_version=$(echo $eei_image_to_publish | awk -F'[/:]' '{print $3}' | awk -F'|' '{print $1}')
    echo "eei_image_name=$eei_image_name - eei_image_version=$eei_image_version"
else
    echo "Invalid index. Please enter a valid index. eei_image_hash[$eei_index] does not exist"
    exit
fi

#========================
#PUBLISH TO PAH  $env
AUTHFILE="config_aaphub_${env}/config_aaphub_auth.json"
#echo "# Log to th image registry aaphub=$aaphub"
#podman login $aaphub --authfile=$AUTHFILE

echo "# Publishing image ${aaphub}/${eei_image_name}:${eei_image_version} to the PAH $aaphub"
podman push --authfile=$AUTHFILE ${aaphub}/${eei_image_name}:${eei_image_version} ${aaphub}/${eei_image_name}:${eei_image_version}

echo "# Tagging as tag=$tag image ${aaphub}/${eei_image_name}:${eei_image_version}"
podman tag ${aaphub}/${eei_image_name}:${eei_image_version} ${aaphub}/${eei_image_name}:$tag

echo "# Publishing image ${aaphub}/${eei_image_name}:$tag to the PAH ${aaphub}"
podman push --authfile=$AUTHFILE ${aaphub}/${eei_image_name}:$tag ${aaphub}/${eei_image_name}:$tag
#========================

#========================

# echo "# Update image history"
# image_history_file="eei_image_history_folder/eei_image_history_${env}.$(date '+%Y%m%d-%H%M%S')"
# touch ${image_history_file}
# ln -fs $image_history_file eei_image_history_${env}

echo "# Update image history"
image_history_file="eei_image_history_folder/eei_image_history_${env}.$(date '+%Y%m%d-%H%M%S')"
#mv $(readlink -f eei_image_history_${env}) $image_history_file
touch $image_history_file
ln -fs $image_history_file eei_image_history_${env}

# echo "#REPOSITORY|CREATED|ID|TAG" > ${image_history_file}
podman images -n --format "{{.Repository}}|{{.CreatedTime}}|{{.ID}}|{{.Tag}}" --sort created | grep ${aaphub} | sort -b -t'|' -k2 >> ${image_history_file}
#podman images -n --format "{{.Repository}}|{{.CreatedTime}}|{{.ID}}|{{.Tag}}" --filter reference=${aaphub}/${eei_image_name}:${tag} | awk -v tag=$tag -F'|' '$4 ~ tag{print $0}'  | grep ${aaphub} | sort -b -t'|' -k2 >> ${image_history_file}
#cat ${image_history_file}

sort -b -t'|' -k4 ${image_history_file} | awk -F '|' '
  /^#/{print $0}
  !/^#/{line[$3]=sprintf("%s|%s|%s",$1,$2,$3);tag[$3]=sprintf("%s%s ",tag[$3],$4)}
  END{for(i in line){print line[i]"|"tag[i]}}
  ' |  (read -r; printf "%s\n" "$REPLY"; sort -b -t'|' -k2)  > ${image_history_file}.sorted
mv ${image_history_file}.sorted ${image_history_file}
ls -al ${image_history_file}
cat ${image_history_file}

#podman rmi -a
