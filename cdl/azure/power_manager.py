#!/usr/bin/env python3
# This program provides management functionalities of VirtualMachines in Azure
# It will also write what it finds along the way into a cache DB,
#   which it will try to reference first in order to speed up the execution time
#
# tsvetelin.maslarski-ext@ldc.com

import os
import json
from pathlib import Path
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from typing import TextIO, Optional
from decouple import config

class AzureVMManager:
    
    def __init__(self):
        # set the vm name and action from env
        self._vm_name = "GDC1TDTCAUT001"
        self._action = "check"
        self._cache_path = "/tmp/test.json"

        self.cache = self.load_cache()

        # self.credential = DefaultAzureCredential()
        self.credential = ClientSecretCredential(
            tenant_id=config('tenant_id'),
            client_id=config('client_id'),
            client_secret=config('client_secret')
        )

        self.vm_info = self.cache.get(self._vm_name)

    @property
    def vm_name(self):
        return self._vm_name

    @property
    def action(self):
        return self._action

    @property
    def cache_path(self):
        return self._cache_path

    def load_cache(self):
        # loads cache from file, or returns empty if not found or invalid
        try:
            with open(self._cache_path, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self):
        # saves the cache dictionary to the cache path
        Path(os.path.dirname(self._cache_path)).mkdir(parents=True, exist_ok=True)
        with open(self._cache_path, "w") as f:  # type: ignore # type: TextIO
            json.dump(self.cache, f, indent=2)  # type: ignore[arg-type]

    def validate_or_discover_vm(self):
        # if VM is cached and validated, use it; otherwise discover it
        if self.vm_info and self.validate_vm_location(self.vm_info):
            return

        self.vm_info = self.search_for_vm()
        if isinstance(self.vm_info, dict):
            self.cache[self._vm_name] = self.vm_info
            self.save_cache()

    def validate_vm_location(self, vm_info):
        # check if VM in cache still exists at the expected subscription/RG
        try:
            client = ComputeManagementClient(self.credential, vm_info["subscription_id"])
            vm = client.virtual_machines.get(vm_info["resource_group"], vm_info["vm_resource_name"])
            computer_name = vm.os_profile.computer_name if vm.os_profile else None
            return computer_name and computer_name.upper() == self._vm_name
        except Exception:
            return False

    def search_for_vm(self):
        # brute-force search for VM by computer name across all subscriptions/RGs
        sub_client = SubscriptionClient(self.credential)
        for sub in sub_client.subscriptions.list():
            # print(f"Searching sub: {sub}\n\n\n")
            sub_id = sub.subscription_id
            compute_client = ComputeManagementClient(self.credential, sub_id)
            resource_client = ResourceManagementClient(self.credential, sub_id)

            try:
                for rg in resource_client.resource_groups.list():
                    print(f"Listing RG: {rg.name}\n\n\n")
                    for vm in compute_client.virtual_machines.list(rg.name):
                        print(f"Checking VM: {vm.name}\n\n\n")
                        vm_details = compute_client.virtual_machines.get(rg.name, vm.name, expand='instanceView')
                        computer_name = vm_details.os_profile.computer_name if vm_details.os_profile else None
                        if computer_name and computer_name.upper() == self._vm_name:
                            return {
                                "subscription_id": sub_id,
                                "resource_group": rg.name,
                                "vm_resource_name": vm.name
                            }
            except Exception:
                continue
        return None

    def perform_action(self):
        # perform the requested action on the VM and return result dictionary
        print(f"Stored info: {self.vm_info}")
        sub_id = self.vm_info["subscription_id"]
        rg = self.vm_info["resource_group"]
        vm_name = self.vm_info["vm_resource_name"]
        compute_client = ComputeManagementClient(self.credential, sub_id)

        try:
            if self._action == "start":
                compute_client.virtual_machines.begin_start(rg, vm_name).wait()
            elif self._action == "stop":
                compute_client.virtual_machines.begin_power_off(rg, vm_name).wait()
            elif self._action == "deallocate":
                compute_client.virtual_machines.begin_deallocate(rg, vm_name).wait()
            elif self._action == "check":
                pass  # the instance view will pull the info anyway, so we don't need extra actions here

            instance_view = compute_client.virtual_machines.instance_view(rg, vm_name)
            power_state = next((s.display_status for s in instance_view.statuses if "PowerState" in s.code), "Unknown")

            return {
                "vm": self._vm_name,
                "resource_group": rg,
                "subscription_id": sub_id,
                "vm_resource_name": vm_name,
                "action": self._action,
                "status": "success",
                "power_state": power_state
            }

        except Exception as e:
            return {
                "vm": self._vm_name,
                "resource_group": rg,
                "subscription_id": sub_id,
                "vm_resource_name": vm_name,
                "action": self._action,
                "status": "failed",
                "error": str(e)
            }

    def run(self):
        # workflow: locate the VM, perform the action, print result
        if not self._vm_name:
            print(json.dumps({"error": "VM_NAME not set"}))
            exit(1)

        self.validate_or_discover_vm()
        if not self.vm_info:
            print(json.dumps({"vm": self._vm_name, "status": "not_found"}))
            exit(1)

        result = self.perform_action()
        print(json.dumps(result))


def main():
    manager = AzureVMManager()
    manager.run()


if __name__ == "__main__":
    main()
