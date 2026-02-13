#!/usr/bin/env python3
"""
Saves a modified file to \\csm1gadmsto001.file.core.windows.net\global-adm-shared\indus\Dyn_IP_validation
with info of IPs if they are dynamic or not. Filename: vm_list_dyn_ip.csv

tsvetelin.maslarski-ext@ldc.com
"""

import os
import csv
import json
import argparse
import tempfile
from azure.identity import DefaultAzureCredential, ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError

# ======================= SETUP ======================= #

parser = argparse.ArgumentParser(description="Check dynamic IP assignments of Azure VMs.")
parser.add_argument("-input", help="Path to the input CSV file", required=False)
parser.add_argument("-output", help="Path to the output CSV file", required=False)
parser.add_argument("-inventory", help="Path to the Azure inventory file", required=False)
args = parser.parse_args()

csv_path = args.input or os.environ.get("INDUS_MASTERFILE_PATH")
output_path = args.output or os.environ.get("INDUS_DYNIP_OUTPUT_PATH")
inventory_path = args.inventory or os.environ.get("INDUS_INVENTORY_PATH")

# parse args and get paths from env if not provided
if not csv_path or not output_path or not inventory_path:
    print(json.dumps({"error": "Missing INDUS_MASTERFILE_PATH, INDUS_DYNIP_OUTPUT_PATH, or INDUS_INVENTORY_PATH"}))
    exit(1)

# ======================= AUTHORITY SWITCHER ======================= #

CHINA_TENANT_ID = os.environ.get("CHINA_TENANT_ID")
CHINA_CLIENT_ID = os.environ.get("CHINA_CLIENT_ID")
CHINA_CLIENT_SECRET = os.environ.get("CHINA_CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
china_prefixes = ["CSM4", "LAB4"]

def authority_switcher(authority):
    """
    Returns a credential object for the specified Azure authority.
    """
    if authority == 'china':
        return ClientSecretCredential(
            tenant_id=CHINA_TENANT_ID,
            client_id=CHINA_CLIENT_ID,
            client_secret=CHINA_CLIENT_SECRET,
            authority=AzureAuthorityHosts.AZURE_CHINA
        )
    else:
        return ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
            # authority=AzureAuthorityHosts.AZURE_PUBLIC_CLOUD
        )

def set_ca_bundle(authority):
    if authority == 'china':
        os.environ['REQUESTS_CA_BUNDLE'] = "/home/GDC1-G-A-UNIX-001/tests/china_root_ca.pem"
        os.environ['SSL_CERT_FILE'] = "/home/GDC1-G-A-UNIX-001/tests/china_root_ca.pem"
    else:
        os.environ.pop('REQUESTS_CA_BUNDLE', None)
        os.environ.pop('SSL_CERT_FILE', None)

# ======================= CLEAN INVENTORY FILE ======================= #

clean_inventory_path = inventory_path + ".clean.csv"

# build a clean inventory file without the #type header
with open(inventory_path, 'r', encoding='utf-8-sig') as original, open(clean_inventory_path, 'w', encoding='utf-8') as cleaned:
    lines = original.readlines()
    if lines and lines[0].startswith("#TYPE"):
        cleaned.writelines(lines[1:])
    else:
        cleaned.writelines(lines)

# ======================= INVENTORY COLLECTION ======================= #

azure_inv_dict = {}
# build a dict of vm_name -> subscription/resource group from inventory
with open(clean_inventory_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        inv_key = row.get("computerName") or row.get("name")
        if not inv_key:
            continue
        vm_name = inv_key.strip().upper()
        resource_id = row.get("ResourceId", "")
        if vm_name and resource_id:
            try:
                parts = resource_id.split("/")
                sub_id = parts[2]
                rg_name = parts[4]
                azure_inv_dict[vm_name] = {
                    "subscription_id": sub_id,
                    "resource_group": rg_name,
                }
            except IndexError:
                continue

# ======================= MASTERFILE ======================= #

# read all vms from the masterfile
with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    vm_data = list(reader)

# ======================= DEBUG LOGGING ======================= #

logfile = os.path.join(tempfile.gettempdir(), "debug_dynip.log")
try:
    with open(logfile, "w", encoding="utf-8") as log:
        log.write("==== Inventory Keys Sample ====\n")
        for i, k in enumerate(azure_inv_dict.keys()):
            if i >= 10:
                break
            log.write(f"{k}\n")

        log.write("\n==== Masterfile Names Sample ====\n")
        for row in vm_data[:10]:
            log.write(f"{row.get('computerName', row.get('name', '')).strip().upper()}\n")
except Exception as e:
    print(f"[WARN] Could not write to debug log: {e}")

print("---- Inventory Sample Keys ----")
print(list(azure_inv_dict.keys())[:10])
print("---- Masterfile Sample Names ----")
print([row.get("computerName", row.get("name", "")).strip().upper() for row in vm_data[:10]])

# ======================= CHECK IP TYPE ======================= #

# main loop: check each vm for dynamic ip
results = []
for row in vm_data:
    vm_name = row.get("computerName", row.get("name", "")).strip().upper()
    row_result = row.copy()
    row_result["dynIP"] = "NO INV DATA"

    inv = azure_inv_dict.get(vm_name)
    if not inv:
        results.append(row_result)
        continue

    sub_id = inv["subscription_id"]
    rg = inv["resource_group"]

    # get sub id and resource group for this vm
    authority = 'china' if any(vm_name.startswith(p) for p in china_prefixes) else 'global'
    set_ca_bundle(authority)
    cred = authority_switcher(authority)

    print(f"Checking {vm_name}")
    print(f"Authority is: {authority}")

    # build correct credential for this vm (china/global)
    try:
        if authority == 'china':
            compute_client = ComputeManagementClient(
                cred, sub_id,
                base_url="https://management.chinacloudapi.cn",
                credential_scopes=["https://management.chinacloudapi.cn/.default"]
            )
            network_client = NetworkManagementClient(
                cred, sub_id,
                base_url="https://management.chinacloudapi.cn",
                credential_scopes=["https://management.chinacloudapi.cn/.default"]
            )
        else:
            compute_client = ComputeManagementClient(cred, sub_id)
            network_client = NetworkManagementClient(cred, sub_id)

        # create azure clients for the right cloud
        vm = compute_client.virtual_machines.get(rg, vm_name)
        nic_refs = vm.network_profile.network_interfaces

        # get vm object and its nics
        for nic_ref in nic_refs:
            nic_name = nic_ref.id.split("/")[-1]
            nic = network_client.network_interfaces.get(rg, nic_name)
            for ip_config in nic.ip_configurations:
                # check first ip config of first nic only
                allocation = ip_config.private_ip_allocation_method
                row_result["dynIP"] = "YES" if allocation.lower() == "dynamic" else "NO"
                print(row_result)
                break
            break

    # handle errors from azure sdk
    except HttpResponseError as hte:
        row_result["dynIP"] = "ERROR"
        print(hte)
    except Exception as e:
        row_result["dynIP"] = "ERROR"
        print(e)


    results.append(row_result)

# ======================= OUTPUT CSV ======================= #

# write results to output csv
fieldnames = list(results[0].keys()) if results else ["name", "dynIP"]
with open(output_path, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
