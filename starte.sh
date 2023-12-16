# shellcheck disable=SC2016
echo '$$$$Changing desktop'
/home/dinky/kill-lxde.sh
# shellcheck disable=SC2016
echo '$$$$Disabling touchpad'
/home/dinky/touch.sh
# shellcheck disable=SC2016
echo '$$$$Starting glipper'
glipper&
# shellcheck disable=SC2016
echo '$$$$Starting Firefox'
firefox&
# shellcheck disable=SC2016
echo '$$$$Starting arandr'
arandr&
# shellcheck disable=SC2016
echo '$$$$Starting Pidgin'
pidgin&
# shellcheck disable=SC2016
echo '$$$$Starting Pulse'
sudo /home/dinky/vpn.sh connect

