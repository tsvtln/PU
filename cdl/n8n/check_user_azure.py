#!/home/n8n-admin/n8n_venv/bin/python
"""
get's user role assignments in a given scope

snippets used from
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/authorization/manage_role_assignment.py
"""
import os

from azure.identity import ClientSecretCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from decouple import config


def main():
    SUBSCRIPTION_ID = "2e78744c-ede2-4e8d-b4ec-f4c63fff5eb5"
    RESOURCE_GROUP = "CDM1KPOCRSG001"
    if RESOURCE_GROUP:
        SCOPE = f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}"
    else:
        SCOPE = f"/subscriptions/{SUBSCRIPTION_ID}"
    TENANT_ID = os.environ.get("TENANT_ID")
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

    if not all([SUBSCRIPTION_ID, SCOPE, TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("Please set SUBSCRIPTION_ID, TENANT_ID, CLIENT_ID, and CLIENT_SECRET environment variables.")
        return

    # authenticate and create client
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    authorization_client = AuthorizationManagementClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID,
        api_version="2018-01-01-preview"
    )

    # this is the user object id that we want to check
    USER_OBJECT_ID = "de9ed18f-3135-45df-ad5c-e6b63f1078e9"
    # List all role assignments for the given scope
    try:
        role_assignments = authorization_client.role_assignments.list_for_scope(SCOPE)
        assignments = list(role_assignments)
        if USER_OBJECT_ID:
            user_assignments = [a for a in assignments if a.principal_id == USER_OBJECT_ID]
            for assignment in user_assignments:
                if 'LDC-Root' in assignment.id:
                    print('OK')
                else:
                    print('NOK')

    except Exception as e:
        print(f"Error listing role assignments: {e}")


if __name__ == "__main__":
    main()