#!/bin/bash
##############################################################################################
# Install Ansible and required collections for AWX CAAC
##############################################################################################

set -e

echo "Installing Ansible dependencies..."
echo ""

# Check if ansible-playbook is available
if command -v ansible-playbook &> /dev/null; then
    echo "[OK] ansible-playbook is already installed"
    ansible --version | head -n 1
else
    echo "Installing ansible-core..."
    pipx install ansible-core
    echo "[OK] ansible-core installed"
fi

echo ""
echo "Installing required Ansible collections..."
ansible-galaxy collection install -r requirements.yml --force

echo ""
echo "[OK] Dependencies installed successfully"
echo ""
echo "You can now run: ./launch_awx_caac.sh -i inventory_demo.yml --ask-vault-pass"

##############################################################################################
