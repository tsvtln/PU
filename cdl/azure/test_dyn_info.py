#!/usr/bin/env python3
import os
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from decouple import config
from azure.core.exceptions import ResourceNotFoundError

# Auth
credential = ClientSecretCredential(
    tenant_id=config('tenant_id'),
    client_id=config('client_id'),
    client_secret=config('client_secret')
)

# Set manually
subscription_id = "93646852-84e4-4024-8598-7bee49d485c7"
resource_group = "CSM1VMONRSG001"
# subscription_id = "2e78744c-ede2-4e8d-b4ec-f4c63fff5eb5"
# resource_group = "CDM1KAPPSUB001"

# Clients
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)

print("Listing all VMs in RG:", resource_group)
for vm in compute_client.virtual_machines.list(resource_group):
    print(f"\n--> Resource VM name: {vm.name}")

    # Get VM details
    details = compute_client.virtual_machines.get(resource_group, vm.name, expand='instanceView')
    print(details)
    if details.os_profile:
        print("   > Computer name:", details.os_profile.computer_name)
        print("   > Power state  :", details.instance_view.statuses[1].display_status)

    # Get NICs
    for nic_ref in vm.network_profile.network_interfaces:
        try:
            nic_name = nic_ref.id.split('/')[-1]
            nic = network_client.network_interfaces.get(resource_group, nic_name)

            for ip_config in nic.ip_configurations:
                alloc_method = ip_config.private_ip_allocation_method
                private_ip = ip_config.private_ip_address
                print(f"   > NIC: {nic.name}")
                print(f"      - Private IP       : {private_ip}")
                print(f"      - Allocation method: {alloc_method}")
        except ResourceNotFoundError as rnf:
            # Handle the case where the NIC is not found
            print(f"Resource {nic_name} not found.")
        except Exception as e:
            print(f"Unexpected Error: {e}")
