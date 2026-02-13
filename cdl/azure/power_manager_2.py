#!/usr/bin/env python3
# Only does power actions without searching for the VM
#
# tsvetelin.maslarski-ext@ldc.com


import os
import json
import time
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from decouple import config

class AzureVMManager:

    def __init__(self):
        # get values from env
        self._vm_name = "CSM1KPOCVMW928"
        self._action = "start"

        # static map for known vm info
        self.vm_map = {
            "CSM1KPOCVMW928": {
                "subscription_id": "2e78744c-ede2-4e8d-b4ec-f4c63fff5eb5",
                "resource_group": "cdm1kpocrsg001",
                "vm_resource_name": "CSM1KPOCVMW928"
            }
        }

        # self.credential = DefaultAzureCredential()
        self.credential = ClientSecretCredential(
            tenant_id=config('TENANT_ID'),
            client_id=config('CLIENT_ID'),
            client_secret=config('CLIENT_SECRET'),
        )

        # fetch info from map
        self.vm_info = self.vm_map.get(self._vm_name)

    def perform_action(self):
        # perform the requested action on the VM and return result dictionary
        sub_id = self.vm_info["subscription_id"]
        rg = self.vm_info["resource_group"]
        vm_name = self.vm_info["vm_resource_name"]
        compute_client = ComputeManagementClient(self.credential, sub_id)

        try:
            # always fetch status first
            instance_view = compute_client.virtual_machines.instance_view(rg, vm_name)
            power_state = next((s.display_status for s in instance_view.statuses if "PowerState" in s.code), "Unknown")

            # skip if already desired state
            if self._action == "start" and power_state == "VM running":
                return self._result("skipped", power_state)
            elif self._action == "stop" and power_state == "VM stopped":
                return self._result("skipped", power_state)
            elif self._action == "deallocate" and power_state == "VM deallocated":
                return self._result("skipped", power_state)

            if self._action == "start":
                # send start signal, don't wait
                compute_client.virtual_machines.begin_start(rg, vm_name)
                # poll status
                max_wait = 90
                interval = 5
                elapsed = 0

                while elapsed < max_wait:
                    time.sleep(interval)
                    elapsed += interval

                    instance_view = compute_client.virtual_machines.instance_view(rg, vm_name)
                    power_state = next((s.display_status for s in instance_view.statuses if "PowerState" in s.code), "Unknown")

                    if power_state == "VM running":
                        return self._result("success", power_state)

                return self._result("timeout", power_state, f"VM did not reach 'running' in {max_wait}s")

            elif self._action == "stop":
                compute_client.virtual_machines.begin_power_off(rg, vm_name).wait()
            elif self._action == "deallocate":
                compute_client.virtual_machines.begin_deallocate(rg, vm_name).wait()
            elif self._action == "check":
                pass  # no-op, already fetched status above

            # refresh status
            instance_view = compute_client.virtual_machines.instance_view(rg, vm_name)
            power_state = next((s.display_status for s in instance_view.statuses if "PowerState" in s.code), "Unknown")

            return self._result("success", power_state)

        except Exception as e:
            return self._result("failed", "Unknown", str(e))

    def _result(self, status, power_state, error_msg=None):
        # builds final result json
        result = {
            "vm": self._vm_name,
            "resource_group": self.vm_info["resource_group"],
            "subscription_id": self.vm_info["subscription_id"],
            "vm_resource_name": self.vm_info["vm_resource_name"],
            "action": self._action,
            "status": status,
            "power_state": power_state
        }
        if error_msg:
            result["error"] = error_msg
        return result

    def run(self):
        # check vm exists in map first
        if not self._vm_name:
            print(json.dumps({"error": "VM_NAME not set"}))
            exit(1)

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
