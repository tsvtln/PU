#!/bin/bash
##############################################################################################
# Test SSH connection and auth file deployment
# Usage: ./test_ssh_connection.sh prod csm1patwexe001
##############################################################################################

env=$1
ee_server=$2

if [ -z "$env" ] || [ -z "$ee_server" ]; then
  echo "Usage: $0 [prod|valid] [server_name]"
  echo "Example: $0 prod csm1patwexe001"
  exit 1
fi

case $env in
  'prod')
    aaphub='csm1patwhub001.d1.ad.local'
  ;;
  'valid')
    aaphub='csm1vatwhub001.d1.ad.local'
  ;;
  *)
    echo "Invalid environment: $env"
    exit 1
  ;;
esac

aapuser="atwaap${env}"
rsa_key=~/.ssh/id_rsa_${env}
AUTHFILE="config_aaphub_${env}/config_aaphub_auth.json"

echo "========================================"
echo "Testing SSH connection to: $ee_server"
echo "User: $aapuser"
echo "Key: $rsa_key"
echo "Auth file: $AUTHFILE"
echo "========================================"
echo ""

echo "Test 1: Check local auth file"
if [ -f "$AUTHFILE" ]; then
  echo "[OK] Auth file exists: $AUTHFILE"
  ls -la "$AUTHFILE"
else
  echo "[FAIL] Auth file NOT found: $AUTHFILE"
  exit 1
fi
echo ""

echo "Test 2: Check SSH key permissions"
if [ -f "$rsa_key" ]; then
  echo "[OK] SSH key exists: $rsa_key"
  ls -la "$rsa_key"
else
  echo "[FAIL] SSH key NOT found: $rsa_key"
  exit 1
fi
echo ""

echo "Test 3: Basic SSH connectivity"
if ssh -i $rsa_key -o ConnectTimeout=5 -o BatchMode=yes ${aapuser}@$ee_server "echo 'SSH connection OK'" 2>&1; then
  echo "[OK] SSH connection successful"
else
  echo "[FAIL] SSH connection failed"
  echo "Try verbose mode: ssh -vvv -i $rsa_key ${aapuser}@$ee_server"
  exit 1
fi
echo ""

echo "Test 4: Test SCP of auth file"
if scp -i $rsa_key $AUTHFILE ${aapuser}@$ee_server:~/config_aaphub_auth.json.test; then
  echo "[OK] SCP successful"
else
  echo "[FAIL] SCP failed"
  exit 1
fi
echo ""

echo "Test 5: Verify file on remote server"
ssh -i $rsa_key ${aapuser}@$ee_server "ls -la ~/config_aaphub_auth.json.test && cat ~/config_aaphub_auth.json.test"
echo ""

echo "Test 6: Test sudo access"
if ssh -i $rsa_key ${aapuser}@$ee_server "sudo -n whoami" 2>&1 | grep -q "root"; then
  echo "[OK] Sudo access OK (passwordless)"
else
  echo "[WARN] Sudo may require password or TTY"
  ssh -i $rsa_key ${aapuser}@$ee_server "sudo whoami"
fi
echo ""

echo "Test 7: Test switching to awx user"
ssh -i $rsa_key ${aapuser}@$ee_server "sudo su - awx -c 'whoami && pwd'"
echo ""

echo "Test 8: Test podman access as awx user"
ssh -i $rsa_key ${aapuser}@$ee_server "sudo su - awx -c 'podman images | head -5'"
echo ""

echo "Test 9: Full command sequence test"
eei_image_name="eei_ldc_standard_216"
tag="poc"

ssh -i $rsa_key ${aapuser}@$ee_server << ENDSSH
echo "==> Copying auth file to /var/lib/awx/"
sudo cp ~/config_aaphub_auth.json.test /var/lib/awx/config_aaphub_auth.json.test
sudo chown awx:awx /var/lib/awx/config_aaphub_auth.json.test
sudo chmod 600 /var/lib/awx/config_aaphub_auth.json.test
echo "==> Verifying file"
sudo ls -la /var/lib/awx/config_aaphub_auth.json.test
echo "==> Testing podman login as awx user"
sudo su - awx -c "podman login --authfile=/var/lib/awx/config_aaphub_auth.json.test ${aaphub}"
ENDSSH

echo ""
echo "========================================"
echo "All tests completed!"
echo "========================================"

