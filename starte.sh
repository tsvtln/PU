echo '$$$$Changing desktop'
/home/dinky/kill-lxde.sh
echo '$$$$Disabling touchpad'
/home/dinky/touch.sh
echo '$$$$Starting glipper'
glipper&
echo '$$$$Starting Firefox'
firefox&
echo '$$$$Starting arandr'
arandr&
echo '$$$$Starting Pidgin'
pidgin&
echo '$$$$Starting Pulse'
sudo /home/dinky/vpn.sh connect

