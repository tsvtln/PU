#!/bin/bash
##############################################################################################
# AWX Config-as-Code Launch Script (Wrapper that removes --eei parameters)

# Set environment
env="demo"

# Filter out --eei and awx_ee:latest parameters
filtered_params=""
skip_next=false

for param in "$@"; do
    if [ "$skip_next" = true ]; then
        skip_next=false
        continue
    fi

    if [ "$param" = "--eei" ]; then
        skip_next=true
        continue
    fi

    # Skip standalone awx_ee:latest
    if [ "$param" = "awx_ee:latest" ]; then
        continue
    fi

    filtered_params="$filtered_params $param"
done

if [ -n "$filtered_params" ]; then
  additional_param="-- $filtered_params"
else
  additional_param=""
fi

dir=$(dirname "$0")
echo "Launch AWX config-as-code : $dir/launch_awx_caac_core.sh -e $env $additional_param"
$dir/launch_awx_caac_core.sh -e $env $additional_param

##############################################################################################
