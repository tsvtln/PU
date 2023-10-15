net stop w32time
w32tm /config /syncfromflags:manual /manualpeerlist:ntp.hchosting.nl /update
w32tm /config /reliable:yes
net start w32time
w32tm /query /configuration