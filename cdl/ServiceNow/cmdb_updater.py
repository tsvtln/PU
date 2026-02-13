#!/usr/bin/env python3

"""
This program updates the CMDB status depending on the step in the decommissioning process as follows:

- Update the CMDB status for a node to "Pending decommission"
- Change the patching group field in CMDB for a node to "to_retired"
- Update the CMDB status for a node to "Retired" and "Non-Operational"

tsvetelin.maslarski-ext@ldc.com
"""

import requests
import json
import argparse


class CMDBUpdater:
    def __init__(self, step, cmdb_user, cmdb_password, cmdb_node_name, dev=False):
        self.step = step
        self.__cmdb_user = cmdb_user
        self.__cmdb_password = cmdb_password
        self.cmdb_node_name = cmdb_node_name
        self.cmdb_url_dev = "https://ldcdev.service-now.com"
        self.cmdb_url_prod = "https://ldc.service-now.com"
        self._headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.cmdb_url = self.cmdb_url_dev if dev else self.cmdb_url_prod
        self._result = {'msg': '', 'failed': False}
        self.deployment = {
            'pending_decommission': self.pending_decommission,
            'to_retired': self.to_retired,
            'retired': self.retired
        }
        self.initializer()
        self.printer()

    @property
    def cmdb_user(self):
        return self.__cmdb_user

    @cmdb_user.setter
    def cmdb_user(self, value):
        self.__cmdb_user = value

    @property
    def cmdb_password(self):
        return self.__cmdb_password

    @cmdb_password.setter
    def cmdb_password(self, value):
        self.__cmdb_password = value

    def __str__(self):
        return self.printer()

    def initializer(self):
        try:
            self.deployment[self.step]()
        except KeyError:
            self._result['msg'] = 'Invalid Call.'
            self._result['failed'] = True

    def printer(self):
        return json.dumps(self._result)

    def response_handler(self, response):

        action_map = {
            'pending_decommission': 'Pending decommission',
            'to_retired': 'To Retired',
            'retired': 'Retired'
        }

        if response.status_code not in [200, 202]:

            try:
                error = response.json()
            except Exception:
                error = response.text

            self._result['msg'] = (f"Failed to update CMDB status to '{action_map[self.step]}' for {self.cmdb_node_name}. "
                                   f"Response Status: {response.status_code}"
                                   f"Response Headers: {response.headers}"
                                   f"Error: {error}")
            self._result['failed'] = True
        else:
            data = response.json()
            self._result['msg'] = (f"Successfully updated CMDB status to "
                                   f"'{action_map[self.step]}' for {self.cmdb_node_name}. "
                                   f"Response: {data.get('result')}")

    # The endpoint group is always the same, but we call a different method depending on the step
    # This function handles the response from the CMDB API
    def _patch_cmdb(self, url):
        response = requests.patch(
            url,
            auth=(self.cmdb_user, self.cmdb_password),
            headers=self._headers,
            data='{\"sys_id\":\"' + self.cmdb_node_name + '\", \"group\":\"_retired\"}',
            verify=False
        )
        self.response_handler(response)

    # Update CMDB with pending decommission status
    def pending_decommission(self):
        url = f"{self.cmdb_url}/api/ldmf2/upsert_ci/update_ci_status"
        self._patch_cmdb(url)

    # Update CMDB patching group to 'to_retired'
    def to_retired(self):
        url = f"{self.cmdb_url}/api/ldmf2/upsert_ci/update_group"
        self._patch_cmdb(url)

    # Update CMDB status for CI to 'Retired' and 'Non-Operational'
    def retired(self):
        url = f"{self.cmdb_url}/api/ldmf2/upsert_ci/to_retired"
        self._patch_cmdb(url)


def runner(step, cmdb_user, cmdb_password, cmdb_node_name, dev=False):
    update_cmdb = CMDBUpdater(str(step), cmdb_user, cmdb_password, cmdb_node_name, dev=dev)
    print(update_cmdb)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update CMDB status for a node")
    parser.add_argument(
        "--step",
        required=True,
        choices=[
            "pending_decommission",
            "to_retired",
            "retired"
        ],
        help="Step in the decommissioning process"
    )
    parser.add_argument("--cmdb_user", required=True, help="CMDB username")
    parser.add_argument("--cmdb_password", required=True, help="CMDB password")
    parser.add_argument("--cmdb_node_name", required=True, help="CMDB node name")
    parser.add_argument("--dev", action="store_true", help="Use development CMDB URL")

    args = parser.parse_args()
    runner(args.step, args.cmdb_user, args.cmdb_password, args.cmdb_node_name, args.dev)
