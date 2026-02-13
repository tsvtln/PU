#!/usr/bin/env python3
# Standalone script to find Recovery Vault and Backup Policy for a given VM using python-decouple and .env file
import json, re
from decouple import config
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.mgmt.recoveryservices import RecoveryServicesClient
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError

SUBSCRIPTION_ID = config("VM_SUBSCRIPTION_ID", default=None)
RESOURCE_GROUP = config("VM_RESOURCE_GROUP", default=None)
VM_NAME = config("VM_NAME", default=None)
AZURE_CLIENT_ID = config("client_id", default=None)
AZURE_TENANT_ID = config("tenant_id", default=None)
AZURE_SECRET = config("client_secret", default=None)
AZURE_CHINA_CLIENT_ID = config('client_id_china', default=None)
AZURE_CHINA_TENANT_ID = config("tenant_id_china", default=None)
AZURE_CHINA_SECRET = config("client_secret_china", default=None)
AZURE_SPACE = config("AZURE_SPACE", default=None)
DEBUG_ENV = config("DEBUG", default=None)
DEBUG = True if DEBUG_ENV and DEBUG_ENV.lower() == 'true' else False
patterns = {
    'protected_item': r'protectedItems/([^/]+)',
    'container_name': r'protectionContainers/([^/]+)',
}

CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
RESOURCE_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}
MGMT_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}

if AZURE_SPACE == 'global':
    credential = ClientSecretCredential(
        tenant_id=AZURE_TENANT_ID,
        client_id=AZURE_CLIENT_ID,
        client_secret=AZURE_SECRET,
    )
elif AZURE_SPACE == 'china':
    credential = ClientSecretCredential(
        tenant_id=AZURE_CHINA_TENANT_ID,
        client_id=AZURE_CHINA_CLIENT_ID,
        client_secret=AZURE_CHINA_SECRET,
        authority=AzureAuthorityHosts.AZURE_CHINA
    )

try:
    vault_client = None
    backup_client = None
    if AZURE_SPACE == 'global':
        backup_client = RecoveryServicesBackupClient(credential, SUBSCRIPTION_ID)
        vault_client = RecoveryServicesClient(credential, SUBSCRIPTION_ID)
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    elif AZURE_SPACE == 'china':
        backup_client = RecoveryServicesBackupClient(credential, SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
        vault_client = RecoveryServicesClient(credential, SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID, **RESOURCE_CLIENT_KWARGS)

    for vault in vault_client.vaults.list_by_subscription_id():
        vault_name = vault.name
        vault_rg = vault.id.split("/")[4]
        containers = backup_client.backup_protected_items.list(
            vault_name=vault_name,
            resource_group_name=vault_rg,
        )
        for container in containers:
            items = backup_client.backup_protected_items.list(
                vault_name=vault_name,
                resource_group_name=vault_rg,
                filter="backupManagementType eq 'AzureIaasVM'"
            )
            for item in items:
                if item.properties.friendly_name.upper() == VM_NAME.upper():
                    if DEBUG:
                        fields = {"item_id": item.id}
                        fields['container_name'] = re.search(patterns['container_name'], fields['item_id']).group(1)
                        fields['protected_item_name'] = re.search(patterns['protected_item'], fields['item_id']).group(1)
                        for k, v in fields.items():
                            print(f'{k}: {v}\n\n')
                        exit(0)
                    else:
                        try:
                            result = {
                                "vault_name": vault_name,
                                "vault_rg": vault_rg,
                                'container_name': re.search(patterns['container_name'], item.id).group(1),
                                'protected_item_name': re.search(patterns['protected_item'], item.id).group(1),
                            }
                            print(json.dumps(result))
                            exit(0)
                        except Exception as e:
                            result = {
                                "error": f"Failed to extract container or protected item name from {item.id}. Error: {e}"
                            }
                            print(json.dumps(result))
                            exit(1)
except HttpResponseError as e:
    print(json.dumps({"error": str(e)}))
    exit(1)

print(json.dumps({"error": f"No backup metadata found for {VM_NAME}"}))
exit(1)

