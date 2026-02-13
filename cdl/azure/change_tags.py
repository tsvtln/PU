#!/usr/bin/env python3
"""
Script to change/update tags on an Azure VM.
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


class AzureVMTagManager:
    """
    Class to manage (add, update, remove) tags on an Azure VM.
    Handles inventory lookup, Azure authentication, and tag operations.
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

    def __init__(self, verbose=False):
        """
        Initialize the AzureVMTagManager.

        Args:
            verbose (bool): Enable verbose output
        """
        self.vm_name = "CSM1KPOCVMW934"
        self.tag_value = "False"
        self.tag_key = "PowerOffPending"
        self.verbose = verbose

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
        """
        Load VM information from the inventory CSV file.

        Args:
            vm_name (str): VM name to search for. Uses instance vm_name if not provided.

        Returns:
            dict: VM information including subscription_id, resource_group, and vm_name
        """
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
        """
        Determine which Azure cloud (global or china) based on VM name.

        Args:
            vm_name (str): VM name to check

        Returns:
            str: 'china' or 'global'
        """
        vm_upper = vm_name.upper()
        if 'CSM4' in vm_upper or 'LAB4' in vm_upper:
            return 'china'
        return 'global'

    def get_compute_client(self, azure_space, subscription_id):
        """
        Create and return an authenticated Azure Compute Management Client.

        Args:
            azure_space (str): 'global' or 'china'
            subscription_id (str): Azure subscription ID

        Returns:
            ComputeManagementClient: Authenticated client
        """
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

    def _initialize_vm_context(self):
        """
        Initialize VM context by loading inventory and setting up Azure client.
        Caches the results for subsequent operations.
        """
        if self._compute_client is not None:
            return  # Already initialized

        # Load VM info from inventory
        vm_info = self.load_inventory(self.vm_name)

        if not vm_info:
            raise ValueError(f"VM '{self.vm_name}' not found in inventory.")

        # Cache the vm info
        self._vm_info = vm_info

        # Determine Azure space
        azure_space = self.determine_azure_space(self.vm_name)
        self._azure_space = azure_space

        # Create compute client
        subscription_id = vm_info["subscription_id"]
        compute_client = self.get_compute_client(azure_space, subscription_id)
        self._compute_client = compute_client

        if self.verbose:
            print(f"VM: {self.vm_name}")
            print(f"Azure Space: {azure_space}")
            print(f"Subscription: {subscription_id}")
            print(f"Resource Group: {vm_info['resource_group']}")

    def get_current_tags(self):
        self._initialize_vm_context()

        try:
            vm = self._compute_client.virtual_machines.get(
                self._vm_info["resource_group"],
                self._vm_info["vm_name"]
            )
            return vm.tags if vm.tags else {}

        except HttpResponseError as e:
            print(f"\nAzure API Error: {e}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            raise

    def set_tag(self):
        self._initialize_vm_context()

        try:
            # Get current VM state to retrieve existing tags
            vm = self._compute_client.virtual_machines.get(
                self._vm_info["resource_group"],
                self._vm_info["vm_name"]
            )
            current_tags = vm.tags if vm.tags else {}

            if self.tag_key in current_tags and current_tags[self.tag_key] == self.tag_value:
                if self.verbose:
                    print(f"\nTag '{self.tag_key}' already exists with value '{self.tag_value}'. No change needed.")
                return {
                    "status": "unchanged",
                    "vm_name": self.vm_name,
                    "tag_key": self.tag_key,
                    "tag_value": self.tag_value,
                    "message": "Tag already exists with the same value"
                }

            old_value = current_tags.get(self.tag_key)

            current_tags[self.tag_key] = self.tag_value

            update_params = {'tags': current_tags}
            self._compute_client.virtual_machines.begin_update(
                self._vm_info["resource_group"],
                self._vm_info["vm_name"],
                update_params
            ).result()

            action = "updated" if old_value is not None else "added"

            if self.verbose:
                if old_value is not None:
                    print(f"\nTag '{self.tag_key}' updated from '{old_value}' to '{self.tag_value}'")
                else:
                    print(f"\nTag '{self.tag_key}' added with value '{self.tag_value}'")

            return {
                "status": "success",
                "action": action,
                "vm_name": self.vm_name,
                "tag_key": self.tag_key,
                "tag_value": self.tag_value,
                "old_value": old_value,
                "message": f"Tag {action} successfully"
            }

        except HttpResponseError as e:
            print(f"\nAzure API Error: {e}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            raise


def main():
    """Main entry point for the script."""

    manager = AzureVMTagManager()
    try:
        result = manager.set_tag()

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
