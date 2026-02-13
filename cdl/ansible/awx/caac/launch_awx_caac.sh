#!/bin/bash
##############################################################################################
# AWX Config-as-Code Launch Script

# Set environment
env="demo"

if [ $# -ge 1 ]; then
  additional_param="-- $*"
else
  additional_param=""
fi

dir=$(dirname "$0")
echo "Launch AWX config-as-code : $dir/launch_awx_caac_core.sh -e $env $additional_param"
$dir/launch_awx_caac_core.sh -e $env $additional_param
