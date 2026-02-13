#!/usr/bin/env python3
"""
Script to retrieve all tags from an Azure VM.
The VM details (subscription, resource group) are read from a CSV inventory file.
SPN authentication is used for both Azure Global and Azure China.

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


class AzureVMTagReader:
    """
    Class to retrieve all tags from an Azure VM.
    Handles inventory lookup, Azure authentication, and tag retrieval.
    """

    # Inventory setup
    INVENTORY_DIR = "/mnt/opcon-archive/Archive/7D/UPD"
    INVENTORY_PREFIX = "azure_VMs_inventory-global-china-"
    CSV_EXT = ".csv"

    # China specific settings
    CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
    MGMT_CLIENT_KWARGS = {
        'base_url': CHINA_ARM_ENDPOINT,
        'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
    }

    def __init__(self):
        """
        Initialize the AzureVMTagReader.

        vm_name (str): Name of the VM to query
        verbose (bool): Enable verbose output
        tag_lookup (str): Specific tag to lookup
        """
        self.vm_name = "csm1kpocvmw934"
        self.verbose = False
        self.tag_lookup = "PowerOffPending"

        # Azure Global SPN credentials
        self.azure_tenant_id = config('tenant_id')
        self.azure_client_id = config('client_id')
        self.azure_client_secret = config('client_secret')

        # Azure China SPN credentials
        self.azure_china_tenant_id = config('tenant_id_china')
        self.azure_china_client_id = config('client_id_china')
        self.azure_china_client_secret = config('client_secret_china')

        # VM info cache
        self._vm_info = None
        self._azure_space = None
        self._compute_client = None

    @staticmethod
    def get_today():
        """Generate a string with the format of the date (today) to match the inventory naming convention."""
        return datetime.today().strftime("%Y%m%d")

    def load_inventory(self, vm_name=None):
        if vm_name is None:
            vm_name = self.vm_name

        if not vm_name:
            raise ValueError("VM name must be provided")

        today_file = f"{self.INVENTORY_PREFIX}{self.get_today()}{self.CSV_EXT}"
        full_path = os.path.join(self.INVENTORY_DIR, today_file)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Inventory not found at: {full_path}")

        with open(full_path, encoding="utf-8-sig") as f:
            lines = f.readlines()

        # Skip metadata line if present
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

    @staticmethod
    def determine_azure_space(vm_name):
        vm_upper = vm_name.upper()
        if 'CSM4' in vm_upper or 'LAB4' in vm_upper:
            return 'china'
        return 'global'

    def get_compute_client(self, azure_space, subscription_id):
        if azure_space == 'global':
            credential = ClientSecretCredential(
                tenant_id=self.azure_tenant_id,
                client_id=self.azure_client_id,
                client_secret=self.azure_client_secret,
            )
            return ComputeManagementClient(credential, subscription_id)

        elif azure_space == 'china':
            credential = ClientSecretCredential(
                tenant_id=self.azure_china_tenant_id,
                client_id=self.azure_china_client_id,
                client_secret=self.azure_china_client_secret,
                authority=AzureAuthorityHosts.AZURE_CHINA
            )
            return ComputeManagementClient(credential, subscription_id, **self.MGMT_CLIENT_KWARGS)

        else:
            raise ValueError(f"Unknown Azure space: {azure_space}")

    def get_vm_tags(self, vm_name=None):
        if vm_name is None:
            vm_name = self.vm_name

        if not vm_name:
            raise ValueError("VM name must be provided")

        # Load VM info from inventory
        vm_info = self.load_inventory(vm_name)

        if not vm_info:
            raise ValueError(f"VM '{vm_name}' not found in inventory.")

        subscription_id = vm_info["subscription_id"]
        resource_group = vm_info["resource_group"]
        vm_resource_name = vm_info["vm_name"]

        # Cache the vm info
        self._vm_info = vm_info

        # Determine Azure space
        azure_space = self.determine_azure_space(vm_name)
        self._azure_space = azure_space

        # Create compute client
        compute_client = self.get_compute_client(azure_space, subscription_id)
        self._compute_client = compute_client

        try:
            vm = compute_client.virtual_machines.get(resource_group, vm_resource_name)

            tags = vm.tags if vm.tags else {}

            if self.verbose:
                if tags:
                    print("\nTags:")
                    for key, value in tags.items():
                        print(f"  {key}: {value}")
                else:
                    print("\nNo tags found on this VM.")
            if tags:
                for tag in tags.items():
                    if tag[0] == self.tag_lookup:
                        return {tag[0]: tag[1]}
            return {"PowerOffPending": "Tag not found"}

        except HttpResponseError as e:
            print(f"\nAzure API Error: {e}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            raise

    def get_tag_value(self, tag_key, vm_name=None):
        """
        Get a specific tag value from the VM.

        Args:
            tag_key (str): The tag key to lookup
            vm_name (str): VM name to query. Uses instance vm_name if not provided.

        Returns:
            str or None: The tag value if found, None otherwise
        """
        result = self.get_vm_tags(vm_name)
        return result['tags'].get(tag_key)

    def has_tag(self, tag_key, vm_name=None):
        """
        Check if VM has a specific tag.

        Args:
            tag_key (str): The tag key to check
            vm_name (str): VM name to query. Uses instance vm_name if not provided.

        Returns:
            bool: True if tag exists, False otherwise
        """
        result = self.get_vm_tags(vm_name)
        return tag_key in result['tags']




def main():
    """Main entry point for the script."""

    try:
        # Create reader instance and get tags
        reader = AzureVMTagReader()
        result = reader.get_vm_tags()

        # Output result as JSON for easy parsing by other tools
        print(json.dumps(result))
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
