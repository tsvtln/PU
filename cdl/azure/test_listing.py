#!/usr/bin/env python3
import os
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError
from decouple import config

# Global Azure environment
credential = ClientSecretCredential(
    tenant_id=config('tenant_id'),
    client_id=config('client_id'),
    client_secret=config('client_secret')
)

subscription_id = "93646852-84e4-4024-8598-7bee49d485c7"
resource_group = "CSM1NGITRSG001"

compute_client = ComputeManagementClient(credential, subscription_id)

try:
    print("Listing all VMs in RG:", resource_group)
    vms = compute_client.virtual_machines.list(resource_group)
    for vm in vms:
        print("Resource VM name:", vm.name)

        details = compute_client.virtual_machines.get(resource_group, vm.name, expand='instanceView')
        if details.os_profile:
            print("Computer name:", details.os_profile.computer_name)
        if details.instance_view and details.instance_view.statuses:
            for status in details.instance_view.statuses:
                if "PowerState" in status.code:
                    print("State:", status.display_status)

except HttpResponseError as e:
    print("Error occurred:", e.message)
    print("Status code:", e.status_code)
