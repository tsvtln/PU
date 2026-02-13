"""
Azure Discovery Module
Handles discovery of subscriptions and resource groups for storage accounts.
"""

from typing import Optional, Tuple
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.core.exceptions import HttpResponseError


class AzureDiscovery:
    """Handles discovery of Azure resources."""

    def __init__(self, credential: ClientSecretCredential, environment: str = 'global'):
        """
        Initialize the discovery service.

        Args:
            credential: Azure credential object
            environment: 'global' or 'china'
        """
        self.credential = credential
        self.environment = environment
        self.base_url = 'https://management.chinacloudapi.cn' if environment == 'china' else None

    def find_storage_account_location(self, storage_account_name: str) -> Optional[Tuple[str, str, str]]:
        """
        Find subscription ID and resource group for a storage account.
        Searches across all accessible subscriptions.

        Args:
            storage_account_name: Name of the storage account to find

        Returns:
            Tuple of (subscription_id, resource_group, display_name) or None if not found
        """
        print(f"\nDiscovering location for storage account '{storage_account_name}'...")

        try:
            # Create subscription client
            if self.base_url:
                sub_client = SubscriptionClient(self.credential, base_url=self.base_url)
            else:
                sub_client = SubscriptionClient(self.credential)

            # Iterate through all subscriptions
            subscriptions = sub_client.subscriptions.list()

            for sub in subscriptions:
                subscription_id = sub.subscription_id
                # print(f"  Checking subscription: {sub.display_name} ({subscription_id})...")
                print('.', end='', flush=True)

                try:
                    # Create storage client for this subscription
                    if self.base_url:
                        storage_client = StorageManagementClient(
                            self.credential, subscription_id, base_url=self.base_url
                        )
                    else:
                        storage_client = StorageManagementClient(self.credential, subscription_id)

                    # List all storage accounts in this subscription
                    storage_accounts = storage_client.storage_accounts.list()

                    for account in storage_accounts:
                        if account.name == storage_account_name:
                            # Extract resource group from account ID
                            # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{name}
                            id_parts = account.id.split('/')
                            resource_group = id_parts[4]

                            print(f"    Found storage account '{storage_account_name}'")
                            print(f"    Subscription: {sub.display_name} ({subscription_id})")
                            print(f"    Resource Group: {resource_group}")

                            return subscription_id, resource_group, sub.display_name

                except HttpResponseError as e:
                    if e.status_code not in [404, 403]:
                        print(f"    Error checking subscription {subscription_id}: {e.message}")
                    continue
                except Exception as e:
                    print(f"    Unexpected error in subscription {subscription_id}: {str(e)}")
                    continue

            print(f"\n  Storage account '{storage_account_name}' not found in any accessible subscription.")
            return None

        except Exception as e:
            print(f"\nError listing subscriptions: {str(e)}")
            return None

    def find_subscription_for_storage_account(self, resource_group: str,
                                             storage_account_name: str) -> Optional[str]:
        """
        Find subscription ID that contains the specified storage account.

        Args:
            resource_group: Resource group name
            storage_account_name: Storage account name

        Returns:
            Subscription ID or None if not found
        """
        print(f"\nDiscovering subscription ID for storage account '{storage_account_name}' "
              f"in resource group '{resource_group}'...")

        try:
            # Create subscription client
            if self.base_url:
                sub_client = SubscriptionClient(self.credential, base_url=self.base_url)
            else:
                sub_client = SubscriptionClient(self.credential)

            # Iterate through all subscriptions
            subscriptions = sub_client.subscriptions.list()

            for sub in subscriptions:
                subscription_id = sub.subscription_id
                # print(f"  Checking subscription: {sub.display_name} ({subscription_id})...")
                print(".", end='.', flush=True)

                try:
                    # Create storage client for this subscription
                    if self.base_url:
                        storage_client = StorageManagementClient(
                            self.credential, subscription_id, base_url=self.base_url
                        )
                    else:
                        storage_client = StorageManagementClient(self.credential, subscription_id)

                    # Try to get the storage account
                    account = storage_client.storage_accounts.get_properties(
                        resource_group, storage_account_name
                    )

                    if account:
                        print(f"    \nFound in subscription: {sub.display_name} ({subscription_id})")
                        return subscription_id

                except HttpResponseError as e:
                    if e.status_code in [404, 403]:
                        continue
                    else:
                        print(f"    \nError checking subscription {subscription_id}: {e.message}")
                        continue
                except Exception as e:
                    print(f"    Unexpected error in subscription {subscription_id}: {str(e)}")
                    continue

            print(f"\n  Storage account '{storage_account_name}' not found in resource group "
                  f"'{resource_group}' in any accessible subscription.")
            return None

        except Exception as e:
            print(f"\nError listing subscriptions: {str(e)}")
            return None

