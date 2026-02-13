"""
CTS - Copy To Storage
Azure File Share Copy Program - Main Entry Point

Copies files from a source file share to a destination file share with verification.
Supports both Azure Global and Azure China environments.

Example usage:

Minimal usage (resource groups auto-discovered):
    python CTS.py --source-storage-account srcaccount --source-share srcshare --dest-storage-account destaccount --dest-share destshare

With resource groups specified (faster):
    python CTS.py --source-storage-account srcaccount --source-resource-group src-rg --source-share srcshare --dest-storage-account destaccount --dest-resource-group dest-rg --dest-share destshare

For Azure China:
    python CTS.py --source-storage-account srcaccount --source-share srcshare --dest-storage-account destaccount --dest-share destshare --environment china

Author: tsvetelin.maslarski-ext@ldc.com
"""

import sys
import argparse
from pathlib import Path
from azure.core.exceptions import HttpResponseError
from tqdm import tqdm
import hashlib
import time

from src.core.azure_auth import AzureAuthenticator
from src.core.azure_discovery import AzureDiscovery
from src.core.azure_storage import AzureStorageManager, FileShareCopier
from src.core.utils import format_bytes, calculate_md5_from_bytes, setup_ssl_verification, check_storage_tiers, check_quota
from src.config.settings import StorageAccountConfig


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Copy files between Azure file shares with verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--source-storage-account', required=True,
                       help='Source storage account name')
    parser.add_argument('--source-resource-group', required=False,
                       help='Source storage account resource group (optional, will be discovered if not provided)')
    parser.add_argument('--source-share', required=True,
                       help='Source file share name')
    parser.add_argument('--dest-storage-account', required=True,
                       help='Destination storage account name')
    parser.add_argument('--dest-resource-group', required=False,
                       help='Destination storage account resource group (optional, will be discovered if not provided)')
    parser.add_argument('--dest-share', required=True,
                       help='Destination file share name')
    parser.add_argument('--environment', choices=['global', 'china'], default='global',
                       help='Azure environment (global or china)')
    parser.add_argument('--dec', action='store_true', default=False,
                       help='Use python-decouple config() instead of os.getenv() for reading .env file')
    parser.add_argument('--enable-ssl-verify', action='store_true', default=False,
                       help='Enable SSL certificate verification (disabled by default for corporate environments)')

    return parser.parse_args()


def discover_storage_location(discovery: AzureDiscovery, account_name: str,
                              resource_group: str = None) -> tuple:
    """
    Discover storage account location.

    Returns:
        Tuple of (subscription_id, resource_group)
    """
    if resource_group:
        # Resource group provided, just find subscription
        print(f"\nResource group provided: {resource_group}")
        subscription_id = discovery.find_subscription_for_storage_account(
            resource_group, account_name
        )

        if not subscription_id:
            raise Exception(
                f"Could not find storage account '{account_name}' "
                f"in resource group '{resource_group}'"
            )

        return subscription_id, resource_group
    else:
        # Discover both subscription and resource group
        result = discovery.find_storage_account_location(account_name)

        if not result:
            raise Exception(f"Could not find storage account '{account_name}'")

        subscription_id, resource_group, _ = result
        return subscription_id, resource_group


def print_banner(title: str):
    """Print a formatted banner."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")


def print_summary(source_config: StorageAccountConfig, dest_config: StorageAccountConfig):
    """Print discovery summary."""
    print_banner("Discovery Complete")
    print(f"  Source:")
    print(f"    Storage Account: {source_config.storage_account}")
    print(f"    Resource Group: {source_config.resource_group}")
    print(f"    Subscription: {source_config.subscription_id}")
    print(f"  Destination:")
    print(f"    Storage Account: {dest_config.storage_account}")
    print(f"    Resource Group: {dest_config.resource_group}")
    print(f"    Subscription: {dest_config.subscription_id}")
    print(f"{'='*70}")


def main():
    """Main execution function."""
    args = parse_arguments()

    # Setup SSL verification
    setup_ssl_verification(disable=not args.enable_ssl_verify)

    print_banner(f"CTS - Copy To Storage | {args.environment.upper()} Environment")

    try:
        # Step 1: Authenticate
        print("\nStep 1: Authenticating...")
        authenticator = AzureAuthenticator(args.environment, args.dec)
        authenticator.load_env_file()
        credential = authenticator.authenticate()
        print(f"  ✓ Authenticated with Service Principal")
        print(f"  Using: {'python-decouple config()' if args.dec else 'os.getenv()'}")

        # Step 2: Discover storage account locations
        print("\nStep 2: Discovering storage account locations...")
        discovery = AzureDiscovery(credential, args.environment)

        # Discover source
        source_sub_id, source_rg = discover_storage_location(
            discovery, args.source_storage_account, args.source_resource_group
        )

        # Discover destination
        dest_sub_id, dest_rg = discover_storage_location(
            discovery, args.dest_storage_account, args.dest_resource_group
        )

        # Create config objects
        source_config = StorageAccountConfig(
            storage_account=args.source_storage_account,
            resource_group=source_rg,
            subscription_id=source_sub_id,
            share_name=args.source_share
        )

        dest_config = StorageAccountConfig(
            storage_account=args.dest_storage_account,
            resource_group=dest_rg,
            subscription_id=dest_sub_id,
            share_name=args.dest_share
        )

        print_summary(source_config, dest_config)

        # Step 3: Get storage account details
        print("\nStep 3: Retrieving storage account details...")
        source_storage_mgr = AzureStorageManager(credential, source_sub_id, args.environment)
        dest_storage_mgr = AzureStorageManager(credential, dest_sub_id, args.environment)

        source_details = source_storage_mgr.get_storage_account_details(source_rg, args.source_storage_account)
        dest_details = dest_storage_mgr.get_storage_account_details(dest_rg, args.dest_storage_account)

        # Check storage tiers
        if not check_storage_tiers(source_details, dest_details):
            print("\nOperation cancelled by user.")
            sys.exit(0)

        # Step 4: Get storage account keys
        print("\nStep 4: Retrieving storage account keys...")
        source_key = source_storage_mgr.get_storage_account_key(source_rg, args.source_storage_account)
        dest_key = dest_storage_mgr.get_storage_account_key(dest_rg, args.dest_storage_account)
        print("  ���� Keys retrieved successfully")

        # Step 5: Create share service clients
        print("\nStep 5: Initializing file share clients...")
        source_service_client = source_storage_mgr.create_share_service_client(
            args.source_storage_account, source_key
        )
        dest_service_client = dest_storage_mgr.create_share_service_client(
            args.dest_storage_account, dest_key
        )
        print("  ✓ Clients initialized")

        # Step 6: Calculate total size
        print(f"\nStep 6: Calculating total size of source share '{args.source_share}'...")
        copier = FileShareCopier(source_service_client, dest_service_client)
        total_size, file_count = copier.calculate_total_size(args.source_share)
        print(f"  Total files: {file_count:,}")
        print(f"  Total size: {total_size:,} bytes ({format_bytes(total_size)})")

        # Step 7: Check destination quota
        print(f"\nStep 7: Checking destination share quota...")
        dest_share_client = dest_service_client.get_share_client(args.dest_share)
        dest_share_props = dest_share_client.get_share_properties()
        dest_quota = dest_share_props.quota * 1024 * 1024 * 1024  # Convert GB to bytes

        print(f"  Destination share quota: {dest_quota:,} bytes ({format_bytes(dest_quota)})")

        if not check_quota(total_size, dest_quota):
            print("\nOperation cancelled.")
            sys.exit(0)

        # Step 8: Copy files
        print_banner("Starting file copy operation...")

        successful, failed = copier.copy_share(
            args.source_share,
            args.dest_share,
            dest_root_dir=args.source_share
        )

        # Print final summary
        print_banner("Copy Operation Complete")
        print(f"  ✓ Successful copies: {successful}")
        if failed > 0:
            print(f"  ✗ Failed copies: {failed}")
        print(f"  Total processed: {successful + failed}")

        if failed > 0:
            print(f"\n⚠ {failed} file(s) failed to copy or verify correctly.")
            sys.exit(1)
        else:
            print(f"\n✓ All files copied and verified successfully!")
            sys.exit(0)

    except HttpResponseError as e:
        print(f"\n✗ Azure API Error: {e.message}")
        print(f"Status code: {e.status_code}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
