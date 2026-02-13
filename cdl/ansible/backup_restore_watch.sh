#!/bin/sh
restore_backup_file='/backup/AAP_backup/automation-platform-backup-latest.tar.gz'

backup_dir='/mnt/AAP_operation/backups/'

log_dir='/backup/logs'

export ANSIBLE_REMOTE_TEMP=/mnt/AAP_operation/ansible_tmp

sudo du -shL $restore_backup_file
while true; do
  for server in CSM1PATWCTL001 CSM1PATWCTL002 CSM1PATWCTL003 CSM1PATWHUB001 CSM1PATWEDA001 CSM1PATWEXE001 CSM1PATWEXE002 CSM1PATWLOG001; do
    ssh -q atwaapprod@$server "
    echo '##############';
    hostname;
#    df -h $backup_dir;
#    sudo ls -al ${backup_dir}restore;
#    sudo ls -al $ANSIBLE_REMOTE_TEMP;
    sudo du -sh $ANSIBLE_REMOTE_TEMP
    "
  done
  echo '============================================'
  echo '============================================'
  sleep 120
done
