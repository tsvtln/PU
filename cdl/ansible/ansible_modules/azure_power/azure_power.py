#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ansible custom module for managing Azure VM power state
# This program provides management functionalities of VirtualMachines in Azure
# It will use the inventory file stored on the share, which is mounted
# on the EE node under /mnt/opcon-archive/Archive/7D/UPD
#
# tsvetelin.maslarski-ext@ldc.com

# ------------- ANSIBLE DOCUMENTATION ---------------
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '3.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: azure_vm_power
version_added: "1.0"
author: "Tsvetelin Maslarski (LDC)"
short_description: Manage Azure VM power state using inventory-based lookup
description:
  - This module allows you to start, stop, or deallocate the power state of Azure virtual machines.
  - The inventory must include the VM's subscriptionId, resourceGroup, and computerName columns.
  - Inventory stored at: \\csm1gadmsto001.file.core.windows.net\global-adm-shared\indus\Inventory_reference
      File name: azure_VMs_inventory-global-china.csv
options:
  vm_name:
    description:
      - Name of the Azure virtual machine (computerName) to manage.
    required: true
    type: str

  action:
    description:
      - Power action to apply to the virtual machine.
    required: true
    type: str
    choices:
      - start
      - stop
      - deallocate

notes:
  - This module must be executed on EE node.
  - Inventory file path is hardcoded inside the module (/mnt/opcon-archive/Archive/7D/UPD/).
  - The inventory file is automatically resolved as: 
      /mnt/opcon-archive/Archive/7D/UPD/azure_VMs_inventory-global-china-<today>.csv
  - The following environment variables must be provided (injected via AAP credentials or vault):
    - AZURE_CLIENT_ID
    - AZURE_CLIENT_SECRET
    - AZURE_TENANT_ID
  - Example of environment injection in a playbook:
      environment:
        AZURE_CLIENT_ID: "{{ client_id }}"
        AZURE_CLIENT_SECRET: "{{ client_secret }}"
        AZURE_TENANT_ID: "{{ tenant_id }}"
'''

EXAMPLES = r'''
- name: Start an Azure VM
  azure_vm_power:
    vm_name: "CSM1KPOCVMW916"
    action: "start"

- name: Stop a VM
  azure_vm_power:
    vm_name: "CSM1KPOCVMW916"
    action: "deallocate"
'''

RETURN = r'''
vm:
  description: The name of the virtual machine.
  type: str
  returned: always

resource_group:
  description: The resource group the VM belongs to.
  type: str
  returned: always

subscription_id:
  description: The subscription ID the VM belongs to.
  type: str
  returned: always

power_state:
  description: The final power state after action.
  type: str
  returned: always

status:
  description: Indicates if the operation was successful.
  type: str
  returned: always
  sample: "success"

error:
  description: Error message if operation failed.
  type: str
  returned: when status == "failed"
'''

from ansible.module_utils.basic import AnsibleModule
import os
import csv
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError


AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
AZURE_SECRET = os.environ.get("AZURE_CLIENT_SECRET")

AZURE_CHINA_CLIENT_ID = os.environ.get('AZURE_CHINA_CLIENT_ID')
AZURE_CHINA_TENANT_ID = os.environ.get("AZURE_CHINA_TENANT_ID")
AZURE_CHINA_SECRET = os.environ.get("AZURE_CHINA_CLIENT_SECRET")

# China specific settings
CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
# kwargs for china clients
RESOURCE_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}
MGMT_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}

# inventory setup
INVENTORY_DIR = "/mnt/opcon-archive/Archive/7D/UPD"
INVENTORY_PREFIX = "azure_VMs_inventory-global-china-"
CSV_EXT = ".csv"

# generates a string for today's tag and loads the file to grep required info
def load_inventory(vm_name):
    today_file = f"{INVENTORY_PREFIX}{get_today()}{CSV_EXT}"
    full_path = os.path.join(INVENTORY_DIR, today_file)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Inventory not found at: {full_path}")

    with open(full_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("name", "").strip().upper() == vm_name.upper():
                return {
                    "subscription_id": row.get("subscriptionId"),
                    "resource_group": row.get("resourceGroup"),
                    "vm_name": row.get("name"),
                }
    return None


# generate a string with the format of the date(today) to match the inventory naming convention
def get_today():
    from datetime import datetime
    return datetime.today().strftime("%Y%m%d")


# gets the current power state (running, stopped etc.)
def get_power_state(instance_view):
    statuses = instance_view.statuses or []
    for s in statuses:
        if "PowerState" in s.code:
            return s.display_status
    return "Unknown"


# execute the called action
def manage_vm(vm_name, action):
    vm_info = load_inventory(vm_name)
    if not vm_info:
        return {"changed": False, "msg": f"VM '{vm_name}' not found in inventory."}

    AZURE_SPACE = 'china' if 'CSM4' in vm_name.upper() or 'LAB4' in vm_name.upper() else 'global'

    if AZURE_SPACE == 'global':
        credentials = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_SECRET,
        )
    elif AZURE_SPACE == 'china':
        credential = ClientSecretCredential(
            tenant_id=AZURE_CHINA_TENANT_ID,
            client_id=AZURE_CHINA_CLIENT_ID,
            client_secret=AZURE_CHINA_SECRET,
            authority=AzureAuthorityHosts.AZURE_CHINA
        )

    if AZURE_SPACE == 'global':
        compute_client = ComputeManagementClient(credentials, vm_info["subscription_id"])
    elif AZURE_SPACE == 'china':
        compute_client = ComputeManagementClient(credential, vm_info["subscription_id"], **MGMT_CLIENT_KWARGS)
    rg = vm_info["resource_group"]
    vm_resource = vm_info["vm_name"]

    try:
        instance_view = compute_client.virtual_machines.instance_view(rg, vm_resource)
        current_state = get_power_state(instance_view)

        if action == "start" and current_state == "VM running":
            return {"changed": False, "msg": "VM is already running."}
        if action in ["stop", "deallocate"] and current_state == "VM deallocated":
            return {"changed": False, "msg": "VM is already deallocated."}

        if action == "start":
            compute_client.virtual_machines.begin_start(rg, vm_resource).wait()
        elif action == "stop":
            compute_client.virtual_machines.begin_power_off(rg, vm_resource).wait()
        elif action == "deallocate":
            compute_client.virtual_machines.begin_deallocate(rg, vm_resource).wait()
        else:
            return {"failed": True, "msg": f"Unsupported action '{action}'"}

        return {"changed": True, "msg": f"{action.title()} request sent.", "vm": vm_resource}

    except HttpResponseError as e:
        return {"failed": True, "msg": f"Azure API error: {str(e)}"}

    except Exception as e:
        return {"failed": True, "msg": f"Unexpected error: {str(e)}"}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type="str", required=True),
            action=dict(type="str", required=True, choices=["start", "stop", "deallocate"]),
        ),
        supports_check_mode=False
    )

    vm_name = module.params["vm_name"]
    action = module.params["action"]

    result = manage_vm(vm_name, action)

    if result.get("failed"):
        module.fail_json(msg=result["msg"])
    else:
        module.exit_json(**result)


if __name__ == "__main__":
    main()