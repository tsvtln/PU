#!/usr/bin/env python3
"""
Script to retrieve all tags from an Azure VM.
The VM details (subscription, resource group) are read from a CSV inventory file.
SPN authentication is used for both Azure Global and Azure China.

Usage:
    python get_vm_tags.py <vm_name>

Example:
    python get_vm_tags.py csm1kpocvmw934

Author: tsvetelin.maslarski-ext@ldc.com
"""

import os
import sys
import csv
import io
import json
from datetime import datetime
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError
from decouple import config

# Inventory setup - matches azure_power_manager.py pattern
INVENTORY_DIR = "/mnt/opcon-archive/Archive/7D/UPD"
INVENTORY_PREFIX = "azure_VMs_inventory-global-china-"
CSV_EXT = ".csv"

# Azure Global SPN credentials
AZURE_TENANT_ID = config('tenant_id')
AZURE_CLIENT_ID = config('client_id')
AZURE_CLIENT_SECRET = config('client_secret')

# Azure China SPN credentials
AZURE_CHINA_TENANT_ID = config('tenant_id_china')
AZURE_CHINA_CLIENT_ID = config('client_id_china')
AZURE_CHINA_CLIENT_SECRET = config('client_secret_china')

# China specific settings
CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
MGMT_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}


def get_today():
    """Generate a string with the format of the date (today) to match the inventory naming convention."""
    return datetime.today().strftime("%Y%m%d")


def load_inventory(vm_name):
    """
    Load VM information from the CSV inventory file.
    Returns a dictionary with subscription_id, resource_group, and vm_name.
    """
    today_file = f"{INVENTORY_PREFIX}{get_today()}{CSV_EXT}"
    full_path = os.path.join(INVENTORY_DIR, today_file)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Inventory not found at: {full_path}")

    with open(full_path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Skip metadata line if present (e.g., "#TYPE Selected.Microsoft.Azure.Commands.Compute.Models.PSVirtualMachine")
    if lines and lines[0].startswith("#TYPE"):
        lines = lines[1:]

    # Rebuild a file-like object with cleaned content
    clean_file = io.StringIO("".join(lines))
    reader = csv.DictReader(clean_file)

    for row in reader:
        if row.get("name", "").strip().upper() == vm_name.upper():
            return {
                "subscription_id": row.get("subscriptionId"),
                "resource_group": row.get("resourceGroup"),
                "vm_name": row.get("name"),
            }

    return None


def determine_azure_space(vm_name):
    """
    Determine if the VM is in Azure China or Azure Global.
    China VMs typically have CSM4 or LAB4 in their name.
    """
    vm_upper = vm_name.upper()
    if 'CSM4' in vm_upper or 'LAB4' in vm_upper:
        return 'china'
    return 'global'


def get_compute_client(azure_space, subscription_id):
    """
    Create and return a ComputeManagementClient based on the Azure space (global or china).
    """
    if azure_space == 'global':
        credential = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET,
        )
        return ComputeManagementClient(credential, subscription_id)

    elif azure_space == 'china':
        credential = ClientSecretCredential(
            tenant_id=AZURE_CHINA_TENANT_ID,
            client_id=AZURE_CHINA_CLIENT_ID,
            client_secret=AZURE_CHINA_CLIENT_SECRET,
            authority=AzureAuthorityHosts.AZURE_CHINA
        )
        return ComputeManagementClient(credential, subscription_id, **MGMT_CLIENT_KWARGS)

    else:
        raise ValueError(f"Unknown Azure space: {azure_space}")


def get_vm_tags(vm_name):
    """
    Main function to retrieve all tags from an Azure VM.

    Steps:
    1. Load VM information from CSV inventory
    2. Determine Azure space (Global or China)
    3. Create appropriate Azure compute client with SPN authentication
    4. Query VM and retrieve tags

    Returns:
        dict: Dictionary containing VM information and tags
    """
    # Step 1: Load VM info from inventory
    print(f"Loading VM information for '{vm_name}' from inventory...")
    vm_info = load_inventory(vm_name)

    if not vm_info:
        raise ValueError(f"VM '{vm_name}' not found in inventory.")

    subscription_id = vm_info["subscription_id"]
    resource_group = vm_info["resource_group"]
    vm_resource_name = vm_info["vm_name"]

    print(f"Found VM in inventory:")
    print(f"  Subscription ID: {subscription_id}")
    print(f"  Resource Group:  {resource_group}")
    print(f"  VM Name:         {vm_resource_name}")

    # Step 2: Determine Azure space
    azure_space = determine_azure_space(vm_name)
    print(f"  Azure Space:     {azure_space.upper()}")

    # Step 3: Create compute client with SPN authentication
    print(f"\nAuthenticating to Azure {azure_space.upper()} using SPN...")
    compute_client = get_compute_client(azure_space, subscription_id)

    # Step 4: Query VM and get tags
    try:
        print(f"\nQuerying Azure API for VM tags...")
        vm = compute_client.virtual_machines.get(resource_group, vm_resource_name)

        tags = vm.tags if vm.tags else {}

        print(f"\nSuccessfully retrieved tags for VM '{vm_name}':")
        print(f"Total tags found: {len(tags)}")

        if tags:
            print("\nTags:")
            for key, value in tags.items():
                print(f"  {key}: {value}")
        else:
            print("\nNo tags found on this VM.")

        result = {
            "vm_name": vm_resource_name,
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "azure_space": azure_space,
            "location": vm.location,
            "tags": tags,
            "tag_count": len(tags)
        }

        return result

    except HttpResponseError as e:
        print(f"\nAzure API Error: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        raise


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python get_vm_tags.py <vm_name>")
        print("\nExample:")
        print("  python get_vm_tags.py csm1natwvmw001")
        sys.exit(1)

    vm_name = sys.argv[1].strip()

    if not vm_name:
        print("Error: VM name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        result = get_vm_tags(vm_name)

        # Output result as JSON for easy parsing by other tools
        print("\n" + "="*70)
        print("JSON Output:")
        print("="*70)
        print(json.dumps(result, indent=2))

        return 0

    except FileNotFoundError as e:
        print(f"\nError: {e}", file=sys.stderr)
        print("Make sure the inventory file exists for today's date.", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
