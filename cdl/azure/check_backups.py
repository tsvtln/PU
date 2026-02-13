#!/usr/bin/python3
import os
# Disable SSL verification for Azure SDK requests (for testing only)
#os.environ["AZURE_CORE_NO_VERIFY_SSL"] = "1"
# If you want to use a custom CA, uncomment the next two lines and set the correct path
#os.environ['REQUESTS_CA_BUNDLE'] = '/etc/pki/ca-trust/source/anchors/Netskope-RootcaCert_2034.crt'
#os.environ['SSL_CERT_FILE'] = '/etc/pki/ca-trust/source/anchors/Netskope-RootcaCert_2034.crt'

import http.client
import logging

from azure.mgmt.resource import ResourceManagementClient
from decouple import config
import json
from azure.identity import ClientSecretCredential
from azure.mgmt.recoveryservices import RecoveryServicesClient
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

# debug shit
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("azure").setLevel(logging.DEBUG)

# get vars
SUBSCRIPTION_ID = "9ad6b51c-c41f-4794-9f4b-86370ea12107"
RESOURCE_GROUP = "CSM4VESBRSG001"
VM_NAME = "CSM4VESBVMW010"
# SUBSCRIPTION_ID = "3af76e9f-ed10-45f0-8ef8-e4b1d4f897c3"
# RESOURCE_GROUP = "CSM1DETLRSG001"
# VM_NAME = "CSM1DETLAPP001"
AZURE_SPACE = 'china'  # global / china

# get secrets from env
TENANT_ID = config('tenant_id')
CLIENT_ID = config('client_id')
CLIENT_SECRET = config('client_secret')
CHINA_TENANT_ID = config('tenant_id_china')
CHINA_CLIENT_ID = config('client_id_china')
CHINA_CLIENT_SECRET = config('client_secret_china')
DEBUG = True

print("AZURE_SPACE:", AZURE_SPACE)
print("CHINA_TENANT_ID:", CHINA_TENANT_ID)
print("CHINA_CLIENT_ID:", CHINA_CLIENT_ID)
if AZURE_SPACE == 'china':
    from azure.identity import AzureAuthorityHosts
    print("Using authority:", AzureAuthorityHosts.AZURE_CHINA)

# auth
if AZURE_SPACE == 'global':
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
elif AZURE_SPACE == 'china':
    from azure.identity import AzureAuthorityHosts
    credential = ClientSecretCredential(
        tenant_id=CHINA_TENANT_ID,
        client_id=CHINA_CLIENT_ID,
        client_secret=CHINA_CLIENT_SECRET,
        authority=AzureAuthorityHosts.AZURE_CHINA
    )
    # Use the same pattern as test_listing_china.py for client instantiation
    CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
    RESOURCE_CLIENT_KWARGS = {
        'base_url': CHINA_ARM_ENDPOINT,
        'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
    }
    MGMT_CLIENT_KWARGS = {
        'base_url': CHINA_ARM_ENDPOINT,
        'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
    }


try:
    found = False
    resource_client = None
    recovery_client = None
    backup_client = None

    # resource, recovery, and backup client initialization based on Azure space
    if AZURE_SPACE == 'global':
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
        recovery_client = RecoveryServicesClient(credential, SUBSCRIPTION_ID)
        backup_client = RecoveryServicesBackupClient(credential, SUBSCRIPTION_ID)
    elif AZURE_SPACE == 'china':
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID, **RESOURCE_CLIENT_KWARGS)
        recovery_client = RecoveryServicesClient(credential, SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
        backup_client = RecoveryServicesBackupClient(credential, SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)


    # go through all resource groups and their recovery services vaults and check for backup items
    for rg in resource_client.resource_groups.list():
        vaults = list(recovery_client.vaults.list_by_resource_group(rg.name))
        for vault in vaults:
            vault_name = vault.name
            if DEBUG:
                print(f"Checking vault: {vault_name} in resource group: {rg.name}")
            try:
                items = list(backup_client.backup_protected_items.list(
                    vault_name=vault_name,
                    resource_group_name=rg.name
                ))
                if DEBUG:
                    print(f"Found {len(items)} protected items in {vault_name}")
                for item in items:
                    if (getattr(item.properties, "backup_management_type", "") == "AzureIaasVM" and
                        getattr(item.properties, "friendly_name", "").upper() == VM_NAME.upper()):
                        found = True
                        break
                if found:
                    break
            except Exception as e:
                if DEBUG:
                    print(f"Error for vault {vault_name} in {rg.name}: {e}")
                continue
        if found:
            break

    print(json.dumps({"has_backup": found}))

except ResourceNotFoundError:
    print(json.dumps({"has_backup": False}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    exit(1)


# OLD check backup logic
# recovery_client = RecoveryServicesClient(credential, SUBSCRIPTION_ID)
# backup_client = RecoveryServicesBackupClient(credential, SUBSCRIPTION_ID)
#
# try:
#     found = False
#     vault_info = {}
#
#     # search vaults in the subscription
#     vaults = recovery_client.vaults.list_by_subscription_id()
#
#     for vault in vaults:
#         vault_name = vault.name
#         vault_rg = vault.id.split("/")[4]
#
#         try:
#             items = backup_client.backup_protected_items.list(
#                 vault_name=vault_name,
#                 resource_group_name=vault_rg
#             )
#         except HttpResponseError:
#             continue  # vault not usable, skip
#
#         for item in items:
#             if not hasattr(item.properties, "friendly_name"):
#                 continue
#
#             if item.properties.friendly_name.upper() == VM_NAME.upper():
#                 found = True
#                 vault_info = {
#                     "vault_name": vault_name,
#                     "vault_rg": vault_rg,
#                     "policy_name": item.properties.policy_id.split("/")[-1]
#                 }
#                 break
#
#         if found:
#             break
#
#     # final output
#     if found:
#         print(json.dumps({
#             "has_backup": True,
#             "vault_info": vault_info
#         }))
#     else:
#         print(json.dumps({
#             "has_backup": False
#         }))
#
# except (ResourceNotFoundError, HttpResponseError) as e:
#     print(json.dumps({"error": str(e)}))
#     exit(1)
# except Exception as e:
#     print(json.dumps({"error": str(e)}))
#     exit(1)
