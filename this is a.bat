echo %time% >> c:\mount_nfs_log.txt
net use N: \\192.168.221.3\rhel >> c:\mount_nfs_log.txt 2>&1
