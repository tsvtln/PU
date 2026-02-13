#!/usr/bin/env python3
"""
Standalone script to trigger Azure VM backup using variables from .env file via python-decouple.
"""
import json
from decouple import config
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.mgmt.recoveryservices import RecoveryServicesClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

result = {'msg': '', 'status': ''}

# VM environment variables from .env
AZURE_CLIENT_ID = config("client_id", default=None)
AZURE_TENANT_ID = config("tenant_id", default=None)
AZURE_SECRET = config("client_secret", default=None)
AZURE_CHINA_CLIENT_ID = config('client_id_china', default=None)
AZURE_CHINA_TENANT_ID = config("tenant_id_china", default=None)
AZURE_CHINA_SECRET = config("client_secret_china", default=None)
AZURE_SPACE = config("AZURE_SPACE", default=None)
VM_SUBSCRIPTION_ID = config("VM_SUBSCRIPTION_ID", default=None)
VM_RESOURCE_GROUP = config("VM_RESOURCE_GROUP", default=None)
VM_NAME = config("VM_NAME", default=None)

# Vault environment variables from .env
VAULT_NAME = config("VAULT_NAME", default=None)
VAULT_RESOURCE_GROUP = config("VAULT_RESOURCE_GROUP", default=None)
VAULT_CONTAINER_NAME = config("VAULT_CONTAINER_NAME", default=None)
VAULT_PROTECTED_ITEM_NAME = config("VAULT_PROTECTED_ITEM_NAME", default=None)
VAULT_FABRIC_NAME = 'Azure'  # Usually "Azure" for Azure IaaS VMs

# China specific settings
CHINA_ARM_ENDPOINT = "https://management.chinacloudapi.cn"
RESOURCE_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}
MGMT_CLIENT_KWARGS = {
    'base_url': CHINA_ARM_ENDPOINT,
    'credential_scopes': [f"{CHINA_ARM_ENDPOINT}/.default"]
}

parameters = {"properties": {"objectType": "AzureIaaSVM"}}

# Create credential object
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

# Initialize clients
if AZURE_SPACE == 'global':
    resource_client = ResourceManagementClient(credential, VM_SUBSCRIPTION_ID)
    compute_client = ComputeManagementClient(credential, VM_SUBSCRIPTION_ID)
    recovery_services_client = RecoveryServicesClient(credential, VM_SUBSCRIPTION_ID)
    recovery_services_backup_client = RecoveryServicesBackupClient(credential, VM_SUBSCRIPTION_ID)
    network_client = NetworkManagementClient(credential, VM_SUBSCRIPTION_ID)
elif AZURE_SPACE == 'china':
    resource_client = ResourceManagementClient(credential, VM_SUBSCRIPTION_ID, **RESOURCE_CLIENT_KWARGS)
    compute_client = ComputeManagementClient(credential, VM_SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
    recovery_services_client = RecoveryServicesClient(credential, VM_SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
    recovery_services_backup_client = RecoveryServicesBackupClient(credential, VM_SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)
    network_client = NetworkManagementClient(credential, VM_SUBSCRIPTION_ID, **MGMT_CLIENT_KWARGS)

def main():
    try:
        backup_now = recovery_services_backup_client.backups.trigger(
            vault_name=VAULT_NAME,
            resource_group_name=VAULT_RESOURCE_GROUP,
            fabric_name=VAULT_FABRIC_NAME,
            container_name=VAULT_CONTAINER_NAME,
            protected_item_name=VAULT_PROTECTED_ITEM_NAME,
            parameters=parameters
        )
        result['msg'], result['status'] = f"Backup triggered successfully for VM {VM_NAME}.", 'success'
    except Exception as e:
        result['msg'], result['status'] = f"Failed to trigger backup for VM {VM_NAME}. Error: {e}", 'failed'
    print(json.dumps(result))

if __name__ == '__main__':
    main()

