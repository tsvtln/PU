#!/usr/bin/env python3
"""
Azure File Share Copy Script
Copies files from a source file share to a destination file share with verification.
Supports both Azure Global and Azure China environments.

Example usage:

Minimal usage (resource groups auto-discovered):
python copy_from_sto.py --source-storage-account srcaccount --source-share srcshare --dest-storage-account destaccount --dest-share destshare

With resource groups specified (faster):
python copy_from_sto.py --source-storage-account srcaccount --source-resource-group src-rg --source-share srcshare --dest-storage-account destaccount --dest-resource-group dest-rg --dest-share destshare

For Azure China:
python copy_from_sto.py --source-storage-account srcaccount --source-share srcshare --dest-storage-account destaccount --dest-share destshare --environment china

Credentials are read from .env file in the same directory.
Both subscription-id and resource-group are automatically discovered when not provided.
SSL certificate verification is disabled by default for corporate environments.

>tsvetelin.maslarski-ext@ldc.com
"""

import sys
import os
import argparse
import hashlib
import ssl
import warnings
import time
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient, ShareServiceClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
# for local testing
from decouple import config
from tqdm import tqdm

# disable insecure warning for clearer logs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# disable SSL verification globally, to avoid issues due to the self-signed certs from netskope
# set environment variables to disable SSL verification
os.environ['AZURE_CLI_DISABLE_CONNECTION_VERIFICATION'] = '1'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

# create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Copy files between Azure file shares with verification'
    )
    parser.add_argument('--source-storage-account', required=True, help='Source storage account name')
    parser.add_argument('--source-resource-group', required=False, help='Source storage account resource group (optional, will be discovered if not provided)')
    parser.add_argument('--source-share', required=True, help='Source file share name')
    parser.add_argument('--dest-storage-account', required=True, help='Destination storage account name')
    parser.add_argument('--dest-resource-group', required=False, help='Destination storage account resource group (optional, will be discovered if not provided)')
    parser.add_argument('--dest-share', required=True, help='Destination file share name')
    parser.add_argument('--environment', choices=['global', 'china'], default='global',
                       help='Azure environment (global or china)')
    parser.add_argument('--dec', action='store_true', default=False,
                       help='Use python-decouple config() instead of os.getenv() for reading .env file')  # used for local testing to read the creds from .env file
    parser.add_argument('--no-ssl-verify', action='store_false', default=True,
                       help='If needed to use custom SSL certificates, enable this.')

    return parser.parse_args()


def load_credentials(environment: str, use_decouple: bool = False) -> tuple:
    """Load credentials from .env file based on environment."""
    # load .env file from the script directory
    script_dir = Path(__file__).parent
    env_path = script_dir / '.env'

    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        sys.exit(1)

    load_dotenv(env_path)

    # get credentials based on environment
    if environment == 'china':
        if use_decouple:
            tenant_id = config('tenant_id_china')
            client_id = config('client_id_china')
            client_secret = config('client_secret_china')
        else:
            tenant_id = os.getenv('tenant_id_china')
            client_id = os.getenv('client_id_china')
            client_secret = os.getenv('client_secret_china')
        env_name = 'China'
    else:  # global
        if use_decouple:
            tenant_id = config('tenant_id')
            client_id = config('client_id')
            client_secret = config('client_secret')
        else:
            tenant_id = os.getenv('tenant_id')
            client_id = os.getenv('client_id')
            client_secret = os.getenv('client_secret')
        env_name = 'Global'

    # remove quotes if present (only needed when using os.getenv)
    if not use_decouple:
        if tenant_id:
            tenant_id = tenant_id.strip('"')
        if client_id:
            client_id = client_id.strip('"')
        if client_secret:
            client_secret = client_secret.strip('"')

    if not tenant_id or not client_id or not client_secret:
        print(f"Error: Missing credentials for {env_name} environment in .env file")
        print(f"Required variables: tenant_id{'_china' if environment == 'china' else ''}, "
              f"client_id{'_china' if environment == 'china' else ''}, "
              f"client_secret{'_china' if environment == 'china' else ''}")
        sys.exit(1)

    return tenant_id, client_id, client_secret


def get_credential(environment: str, use_decouple: bool = False) -> ClientSecretCredential:
    """Get credential from .env file based on environment."""
    try:
        tenant_id, client_id, client_secret = load_credentials(environment, use_decouple)

        # set authority based on environment
        if environment == 'china':
            authority = 'https://login.chinacloudapi.cn'
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                authority=authority
            )
        else:  # global
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )

        print(f"  Authenticated with Service Principal")
        print(f"  Using: {'python-decouple config()' if use_decouple else 'os.getenv()'}")
        print(f"  Tenant ID: {tenant_id}")
        print(f"  Client ID: {client_id}")

        return credential

    except Exception as e:
        print(f"Error getting credential: {str(e)}")
        sys.exit(1)


def find_storage_account_location(credential, storage_account_name: str,
                                  environment: str) -> Optional[Tuple[str, str, str]]:
    """
    Find the subscription ID and resource group that contains the specified storage account.
    Searches across all accessible subscriptions.
    Returns tuple of (subscription_id, resource_group, display_name) or None if not found.
    """
    print(f"\nDiscovering location for storage account '{storage_account_name}'...")

    # set base URL based on environment
    if environment == 'china':
        base_url = 'https://management.chinacloudapi.cn'
    else:
        base_url = None  # use default

    try:
        # create subscription client
        if base_url:
            sub_client = SubscriptionClient(credential, base_url=base_url)
        else:
            sub_client = SubscriptionClient(credential)

        # iterate through all subscriptions
        subscriptions = sub_client.subscriptions.list()

        for sub in subscriptions:
            subscription_id = sub.subscription_id
            # print(f"  Checking subscription: {sub.display_name} ({subscription_id})...")

            try:
                # create storage client for this subscription
                if base_url:
                    storage_client = StorageManagementClient(
                        credential, subscription_id, base_url=base_url
                    )
                else:
                    storage_client = StorageManagementClient(credential, subscription_id)

                # list all storage accounts in this subscription
                storage_accounts = storage_client.storage_accounts.list()

                for account in storage_accounts:
                    if account.name == storage_account_name:
                        # extract resource group from account ID
                        # format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{name}
                        id_parts = account.id.split('/')
                        resource_group = id_parts[4]  # resource group is at index 4

                        print(f"    Found storage account '{storage_account_name}'")
                        print(f"    Subscription: {sub.display_name} ({subscription_id})")
                        print(f"    Resource Group: {resource_group}")

                        return subscription_id, resource_group, sub.display_name

            except HttpResponseError as e:
                # error listing storage accounts in this subscription, continue
                if e.status_code not in [404, 403]:
                    print(f"    Error checking subscription {subscription_id}: {e.message}")
                continue
            except Exception as e:
                # unexpected error, print but continue
                print(f"    Unexpected error in subscription {subscription_id}: {str(e)}")
                continue

        # not found in any subscription
        print(f"\n  Storage account '{storage_account_name}' not found in any accessible subscription.")
        return None

    except Exception as e:
        print(f"\nError listing subscriptions: {str(e)}")
        return None


def find_subscription_for_storage_account(credential, resource_group: str,
                                         storage_account_name: str,
                                         environment: str) -> Optional[str]:
    """
    Find the subscription ID that contains the specified storage account.
    Searches across all accessible subscriptions.
    """
    print(f"\nDiscovering subscription ID for storage account '{storage_account_name}' in resource group '{resource_group}'...")

    # set base URL based on environment
    if environment == 'china':
        base_url = 'https://management.chinacloudapi.cn'
    else:
        base_url = None  # use default

    try:
        # create subscription client
        if base_url:
            sub_client = SubscriptionClient(credential, base_url=base_url)
        else:
            sub_client = SubscriptionClient(credential)

        # iterate through all subscriptions
        subscriptions = sub_client.subscriptions.list()

        for sub in subscriptions:
            subscription_id = sub.subscription_id
            # print(f"  Checking subscription: {sub.display_name} ({subscription_id})...")

            try:
                # create storage client for this subscription
                if base_url:
                    storage_client = StorageManagementClient(
                        credential, subscription_id, base_url=base_url
                    )
                else:
                    storage_client = StorageManagementClient(credential, subscription_id)

                # try to get the storage account
                account = storage_client.storage_accounts.get_properties(
                    resource_group, storage_account_name
                )

                if account:
                    print(f"    Found in subscription: {sub.display_name} ({subscription_id})")
                    return subscription_id

            except HttpResponseError as e:
                # storage account not in this subscription, continue searching
                if e.status_code in [404, 403]:
                    continue
                else:
                    # other error, print but continue
                    print(f"    Error checking subscription {subscription_id}: {e.message}")
                    continue
            except Exception as e:
                # unexpected error, print but continue
                print(f"    Unexpected error in subscription {subscription_id}: {str(e)}")
                continue

        # not found in any subscription
        print(f"\n  Storage account '{storage_account_name}' not found in resource group '{resource_group}' in any accessible subscription.")
        return None

    except Exception as e:
        print(f"\nError listing subscriptions: {str(e)}")
        return None


def get_storage_account_details(storage_client: StorageManagementClient,
                                resource_group: str,
                                account_name: str) -> dict:
    """Get storage account details including SKU tier."""
    try:
        account = storage_client.storage_accounts.get_properties(resource_group, account_name)
        return {
            'name': account.name,
            'sku_name': account.sku.name,
            'sku_tier': account.sku.tier,
            'location': account.location,
            'kind': account.kind
        }
    except HttpResponseError as e:
        print(f"Error getting storage account details: {e.message}")
        raise


def check_storage_tiers(source_details: dict, dest_details: dict) -> bool:
    """
    Check if source is Premium and destination is Standard.
    Returns True if it's OK to continue.
    """
    source_tier = source_details['sku_tier']
    dest_tier = dest_details['sku_tier']

    print(f"\nSource storage account: {source_details['name']}")
    print(f"  SKU: {source_details['sku_name']}, Tier: {source_tier}")

    print(f"\nDestination storage account: {dest_details['name']}")
    print(f"  SKU: {dest_details['sku_name']}, Tier: {dest_tier}")

    if source_tier == 'Premium' and dest_tier == 'Standard':
        print("\nSource is Premium and destination is Standard - OK to continue")
        return True
    else:
        print(f"\nWarning: Source tier is '{source_tier}' and destination tier is '{dest_tier}' - Will not continue!")
        # response = input("Continue anyway? (yes/no): ")
        # return response.lower() in ['yes', 'y']
        return False


def get_storage_account_key(storage_client: StorageManagementClient,
                            resource_group: str,
                            account_name: str) -> str:
    """Get storage account key."""
    keys = storage_client.storage_accounts.list_keys(resource_group, account_name)
    return keys.keys[0].value


def calculate_md5(file_client: ShareFileClient) -> str:
    """Calculate MD5 hash of a file in Azure File Share."""
    md5_hash = hashlib.md5()

    # download file in chunks and calculate hash
    download_stream = file_client.download_file()
    for chunk in download_stream.chunks():
        md5_hash.update(chunk)

    return md5_hash.hexdigest()


def get_file_share_total_size(share_service_client: ShareServiceClient,
                              share_name: str) -> Tuple[int, int]:
    """
    Calculate total size and count of all files in a file share.
    Returns tuple of (total_size_bytes, file_count)
    """
    total_size = 0
    file_count = 0

    share_client = share_service_client.get_share_client(share_name)

    def traverse_directory(directory_client: ShareDirectoryClient, path: str = ""):
        nonlocal total_size, file_count

        try:
            items = directory_client.list_directories_and_files()
            for item in items:
                item_path = f"{path}/{item['name']}" if path else item['name']

                if item['is_directory']:
                    # recursively traverse subdirectory
                    subdir_client = share_client.get_directory_client(item_path)
                    traverse_directory(subdir_client, item_path)
                else:
                    # it's a file
                    file_client = share_client.get_file_client(item_path)
                    properties = file_client.get_file_properties()
                    total_size += properties.size
                    file_count += 1
        except Exception as e:
            print(f"Error traversing directory {path}: {str(e)}")

    # start from root
    root_dir_client = share_client.get_directory_client("")
    traverse_directory(root_dir_client)

    return total_size, file_count


def copy_file_with_verification(source_file_client: ShareFileClient,
                                dest_file_client: ShareFileClient,
                                file_path: str,
                                chunk_size: int = 4 * 1024 * 1024) -> bool:
    """
    Copy a single file and verify with MD5 checksum.
    Handles large files by chunking.
    Returns True if copy was successful and verified.
    """
    try:
        source_props = source_file_client.get_file_properties()
        file_size = source_props.size

        print(f"Copying: {file_path} ({file_size:,} bytes)")

        # Create the file with the correct size first
        dest_file_client.create_file(size=file_size)

        # Download and upload in chunks, and calculate MD5 on the fly
        source_md5 = hashlib.md5()
        offset = 0

        download_stream = source_file_client.download_file()
        bytes_remaining = file_size

        # Initialize progress bar
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Copying {file_path}") as pbar:
            for chunk in download_stream.chunks():
                source_md5.update(chunk)
                dest_file_client.upload_range(chunk, offset=offset, length=len(chunk))
                offset += len(chunk)
                pbar.update(len(chunk))

        source_md5_hex = source_md5.hexdigest()

        # close progress bar explicitly after file copy
        pbar.close()

        print("Starting MD5 verification...")
        start_time = time.time()

        # verify destination file by downloading in chunks and calculating MD5
        dest_md5 = hashlib.md5()
        offset = 0
        dest_download_stream = dest_file_client.download_file()

        for chunk in dest_download_stream.chunks():
            dest_md5.update(chunk)

        dest_md5_hex = dest_md5.hexdigest()
        verification_time = time.time() - start_time
        print(f"MD5 verification completed in {verification_time:.2f} seconds.")

        if source_md5_hex == dest_md5_hex:
            print(f"  Verified: MD5={source_md5_hex}")
            return True
        else:
            print(f"  VERIFICATION FAILED!")
            print(f"  Source MD5: {source_md5_hex}")
            print(f"  Dest MD5:   {dest_md5_hex}")
            return False

    except Exception as e:
        print(f"✗ Error copying file {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def copy_files_recursive(source_share_client, dest_share_client,
                        source_path: str = "", dest_path: str = "") -> Tuple[int, int]:
    """
    Recursively copy all files from source to destination.
    Returns tuple of (successful_count, failed_count)
    """
    successful = 0
    failed = 0

    # get directory clients
    if source_path:
        source_dir_client = source_share_client.get_directory_client(source_path)
    else:
        source_dir_client = source_share_client.get_directory_client("")

    try:
        items = source_dir_client.list_directories_and_files()

        for item in items:
            item_name = item['name']
            source_item_path = f"{source_path}/{item_name}" if source_path else item_name
            dest_item_path = f"{dest_path}/{item_name}" if dest_path else item_name

            if item['is_directory']:
                # create directory in destination
                try:
                    dest_dir_client = dest_share_client.get_directory_client(dest_item_path)
                    dest_dir_client.create_directory()
                    print(f"Created directory: {dest_item_path}")
                except HttpResponseError as e:
                    # directory might already exist - that's okay
                    if 'ResourceAlreadyExists' in str(e) or e.status_code == 409:
                        print(f"Directory already exists: {dest_item_path}")
                    else:
                        print(f"Warning: Error creating directory {dest_item_path}: {e.message}")
                except ResourceNotFoundError:
                    # parent directory doesn't exist
                    print(f"Warning: Parent directory not found for {dest_item_path}")
                except Exception as e:
                    # check if it's a ResourceAlreadyExists error
                    if 'ResourceAlreadyExists' in str(e) or 'already exists' in str(e).lower():
                        print(f"Directory already exists: {dest_item_path}")
                    else:
                        print(f"Warning: Error creating directory {dest_item_path}: {str(e)}")

                # recursively copy subdirectory
                sub_success, sub_failed = copy_files_recursive(
                    source_share_client, dest_share_client,
                    source_item_path, dest_item_path
                )
                successful += sub_success
                failed += sub_failed
            else:
                # copy file
                source_file_client = source_share_client.get_file_client(source_item_path)
                dest_file_client = dest_share_client.get_file_client(dest_item_path)

                if copy_file_with_verification(source_file_client, dest_file_client, source_item_path):
                    successful += 1
                else:
                    failed += 1

    except Exception as e:
        print(f"Error processing directory {source_path}: {str(e)}")
        # maybe don't count this as a failed file if it's just a directory issue, idk
        if 'ResourceAlreadyExists' not in str(e) and 'already exists' not in str(e).lower():
            failed += 1

    return successful, failed


def main():
    """Main execution function."""
    args = parse_arguments()

    # handle SSL certificate verification
    if args.no_ssl_verify:
        import ssl
        import urllib3
        # disable SSL warnings once again, because they pop up
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # Set environment variable to disable SSL verification for Azure SDK
        os.environ['AZURE_CLI_DISABLE_CONNECTION_VERIFICATION'] = '1'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''

    print(f"\n{'='*70}")
    print(f"Azure File Share Copy - {args.environment.upper()} Environment")
    print(f"{'='*70}")

    try:
        # get credential
        print("\nAuthenticating...")
        credential = get_credential(args.environment, args.dec)

        # discover source storage account location (subscription + resource group)
        if args.source_resource_group:
            # resource group provided, just find subscription
            print(f"\nSource resource group provided: {args.source_resource_group}")
            source_subscription_id = find_subscription_for_storage_account(
                credential,
                args.source_resource_group,
                args.source_storage_account,
                args.environment
            )
            source_resource_group = args.source_resource_group

            if not source_subscription_id:
                print(f"\nError: Could not find source storage account '{args.source_storage_account}' in resource group '{args.source_resource_group}'")
                sys.exit(1)
        else:
            # discover both subscription and resource group
            result = find_storage_account_location(
                credential,
                args.source_storage_account,
                args.environment
            )

            if not result:
                print(f"\nError: Could not find source storage account '{args.source_storage_account}'")
                sys.exit(1)

            source_subscription_id, source_resource_group, _ = result

        # discover destination storage account location (subscription + resource group)
        if args.dest_resource_group:
            # resource group provided, just find subscription
            print(f"\nDestination resource group provided: {args.dest_resource_group}")
            dest_subscription_id = find_subscription_for_storage_account(
                credential,
                args.dest_resource_group,
                args.dest_storage_account,
                args.environment
            )
            dest_resource_group = args.dest_resource_group

            if not dest_subscription_id:
                print(f"\nError: Could not find destination storage account '{args.dest_storage_account}' in resource group '{args.dest_resource_group}'")
                sys.exit(1)
        else:
            # discover both subscription and resource group
            result = find_storage_account_location(
                credential,
                args.dest_storage_account,
                args.environment
            )

            if not result:
                print(f"\nError: Could not find destination storage account '{args.dest_storage_account}'")
                sys.exit(1)

            dest_subscription_id, dest_resource_group, _ = result

        print(f"\n{'='*70}")
        print(f"Discovery Complete")
        print(f"  Source:")
        print(f"    Storage Account: {args.source_storage_account}")
        print(f"    Resource Group: {source_resource_group}")
        print(f"    Subscription: {source_subscription_id}")
        print(f"  Destination:")
        print(f"    Storage Account: {args.dest_storage_account}")
        print(f"    Resource Group: {dest_resource_group}")
        print(f"    Subscription: {dest_subscription_id}")
        print(f"{'='*70}")

        # set base URL based on environment
        if args.environment == 'china':
            base_url = 'https://management.chinacloudapi.cn'
            storage_suffix = 'core.chinacloudapi.cn'
        else:
            base_url = None  # use default
            storage_suffix = 'core.windows.net'

        # create storage management clients for source and destination
        if base_url:
            source_storage_client = StorageManagementClient(
                credential, source_subscription_id, base_url=base_url
            )
            dest_storage_client = StorageManagementClient(
                credential, dest_subscription_id, base_url=base_url
            )
        else:
            source_storage_client = StorageManagementClient(credential, source_subscription_id)
            dest_storage_client = StorageManagementClient(credential, dest_subscription_id)

        # get storage account details
        print("\nRetrieving storage account details...")
        source_details = get_storage_account_details(
            source_storage_client, source_resource_group, args.source_storage_account
        )
        dest_details = get_storage_account_details(
            dest_storage_client, dest_resource_group, args.dest_storage_account
        )

        # check storage tiers
        if not check_storage_tiers(source_details, dest_details):
            print("\nOperation cancelled. Can only copy from Premium to Standard.")
            sys.exit(0)

        # get storage account keys
        print("\nRetrieving storage account keys...")
        source_key = get_storage_account_key(
            source_storage_client, source_resource_group, args.source_storage_account
        )
        dest_key = get_storage_account_key(
            dest_storage_client, dest_resource_group, args.dest_storage_account
        )

        # create ShareServiceClient for source and destination
        source_service_client = ShareServiceClient(
            account_url=f"https://{args.source_storage_account}.file.{storage_suffix}",
            credential=source_key,
            connection_verify=False
        )
        dest_service_client = ShareServiceClient(
            account_url=f"https://{args.dest_storage_account}.file.{storage_suffix}",
            credential=dest_key,
            connection_verify=False
        )

        # calculate total size of source files
        print(f"\nCalculating total size of files in source share '{args.source_share}'...")
        total_size, file_count = get_file_share_total_size(source_service_client, args.source_share)
        print(f"Total files: {file_count:,}")
        print(f"Total size: {total_size:,} bytes ({total_size / (1024**3):.2f} GB)")

        # get destination share quota
        dest_share_client = dest_service_client.get_share_client(args.dest_share)
        dest_share_props = dest_share_client.get_share_properties()
        dest_quota = dest_share_props.quota * 1024 * 1024 * 1024  # Convert GB to bytes

        print(f"\nDestination share quota: {dest_quota:,} bytes ({dest_quota / (1024**3):.2f} GB)")

        # check if there's enough space (basic check)
        if total_size > dest_quota:
            print(f"\nWARNING: Source total size ({total_size:,} bytes) exceeds destination quota ({dest_quota:,} bytes)")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("\nOperation cancelled.")
                sys.exit(0)

        # proceed with copy
        print(f"\n{'='*70}")
        print(f"Starting file copy operation...")
        print(f"{'='*70}\n")

        source_share_client = source_service_client.get_share_client(args.source_share)

        # create destination root directory named after source share if not exists
        dest_root_dir_client = dest_share_client.get_directory_client(args.source_share)
        try:
            dest_root_dir_client.create_directory()
            print(f"Created root directory in destination: {args.source_share}")
        except ResourceNotFoundError:
            pass  # Directory may already exist
        except Exception as e:
            if 'ResourceAlreadyExists' not in str(e):
                print(f"Error creating root directory in destination: {str(e)}")
                sys.exit(1)

        # start timing
        start_time = time.time()

        successful, failed = copy_files_recursive(
            source_share_client, dest_share_client,
            source_path="", dest_path=args.source_share
        )

        # end timing
        end_time = time.time()
        total_seconds = end_time - start_time

        # summary
        print(f"\n{'='*70}")
        print(f"Copy Operation Complete")
        print(f"{'='*70}")
        print(f"Successful copies: {successful}")
        print(f"Failed copies: {failed}")
        print(f"Total processed: {successful + failed}")
        print(f"Total time taken: {total_seconds:.2f} seconds")

        if failed > 0:
            print(f"\n{failed} file(s) failed to copy or verify correctly.")
            sys.exit(1)
        else:
            print(f"\nAll files copied and verified successfully!")
            sys.exit(0)

    except HttpResponseError as e:
        print(f"\nAzure API Error: {e.message}")
        print(f"Status code: {e.status_code}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
