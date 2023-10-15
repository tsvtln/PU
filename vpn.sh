#!/bin/bash
URL="https://germany.remoteaccess.com"
#URL="https://uk.remoteaccess.com"
#URL="https://uk.remoteaccess.com/dana-na/auth/url_default/welcome.cgi"
#URL="https://global.remoteaccess.com"
case $1 in

connect)

#exec 3<&0 </dev/null
#read -r var <&3

echo 'Please provide OTP Password: '
stty -echo; read passwd; stty echo
echo 951753${passwd} | openconnect -v -b -q --juniper $URL --user='W21986174' --authgroup='OATH Passcode' --passwd-on-stdin --no-cert-check ;;


disconnect)

#exec 3<&0 </dev/null
#read -r var <&3

killall -s SIGINT openconnect;;

*)
echo 'Usage: vpn.sh [connect|disconnect]'; exit 1 ;;

esac
