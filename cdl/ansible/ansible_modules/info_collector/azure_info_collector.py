#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Ansible custom module to collect info by only providing VM name from Azure
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
short_description: Collects VM info from Azure.
description:
  - Computer name must be provided in order to collect VM info.
  - The program will brute-force search in all available subscriptions to find the VM.
  - If a VM is found the information will be outputted as:
        {
            "subscriptionId": "<subscription_id>",
            "resourceGroup": "<resource_group_id>",
            "name": "vm_name",
            "status": "<power_state>"
        }
notes:
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
- name: Collect VM info
  azure_info_collector:
    vm_name: "CSM1KPOCVMW916"
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
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource import ResourceManagementClient,SubscriptionClient


AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
AZURE_SECRET = os.environ.get("AZURE_CLIENT_SECRET")

def collect_info(vm_name):
    credentials = DefaultAzureCredential()
    sub_client = SubscriptionClient(credentials)
    found = {}

    for sub in sub_client.subscriptions.list():
        sub_id = sub.subscription_id
        compute_client = ComputeManagementClient(credentials, sub_id)
        resource_client = ResourceManagementClient(credentials, sub_id)
        try:
            for rg in resource_client.resource_groups.list():
                for vm in compute_client.virtual_machines.list(rg.name):
                    vm_details = compute_client.virtual_machines.get(rg.name, vm.name, expand='instanceView')
                    computer_name = vm_details.os_profile.computer_name if vm_details.os_profile else None
                    if computer_name and computer_name.upper() == vm_name.upper():
                        power_state =\
                            compute_client.virtual_machines.get(
                                rg.name,
                                vm.name,
                                expand='instanceView').instance_view.statuses[1].display_status
                        found['subscriptionId'] = sub_id
                        found['resourceGroup'] = rg.name
                        found['name'] = vm.name
                        found['status'] = power_state
        except Exception:
            continue
    
    if not found:
        return {'failed': True, 'msg': f"Couldn't find {vm_name}"}
    return {'changed': True, 'msg': found}

def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
        ),
        supports_check_mode=False,
    )

    vm_name = module.params['vm_name']
    result = collect_info(vm_name)

    if result.get('failed'):
        module.fail_json(msg=result['msg'])
    else:
        module.exit_json(**result)

if __name__ == '__main__':
    main()