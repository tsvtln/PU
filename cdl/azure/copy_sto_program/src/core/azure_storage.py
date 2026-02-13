"""
Azure Storage Module
Handles Azure storage account operations and file share copying.
"""

import hashlib
from typing import Tuple, Dict
from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient, ShareServiceClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from tqdm import tqdm
import time


class AzureStorageManager:
    """Manages Azure storage account operations."""

    def __init__(self, credential: ClientSecretCredential, subscription_id: str,
                 environment: str = 'global'):
        """
        Initialize storage manager.

        Args:
            credential: Azure credential object
            subscription_id: Azure subscription ID
            environment: 'global' or 'china'
        """
        self.credential = credential
        self.subscription_id = subscription_id
        self.environment = environment
        self.base_url = 'https://management.chinacloudapi.cn' if environment == 'china' else None
        self.storage_suffix = 'core.chinacloudapi.cn' if environment == 'china' else 'core.windows.net'

        # Create storage management client
        if self.base_url:
            self.storage_client = StorageManagementClient(
                credential, subscription_id, base_url=self.base_url
            )
        else:
            self.storage_client = StorageManagementClient(credential, subscription_id)

    def get_storage_account_details(self, resource_group: str, account_name: str) -> Dict[str, str]:
        """
        Get storage account details including SKU tier.

        Args:
            resource_group: Resource group name
            account_name: Storage account name

        Returns:
            Dictionary with account details
        """
        try:
            account = self.storage_client.storage_accounts.get_properties(resource_group, account_name)
            return {
                'name': account.name,
                'sku_name': account.sku.name,
                'sku_tier': account.sku.tier,
                'location': account.location,
                'kind': account.kind
            }
        except HttpResponseError as e:
            raise Exception(f"Error getting storage account details: {e.message}")

    def get_storage_account_key(self, resource_group: str, account_name: str) -> str:
        """
        Get storage account access key.

        Args:
            resource_group: Resource group name
            account_name: Storage account name

        Returns:
            Storage account key
        """
        keys = self.storage_client.storage_accounts.list_keys(resource_group, account_name)
        return keys.keys[0].value

    def create_share_service_client(self, account_name: str, account_key: str) -> ShareServiceClient:
        """
        Create ShareServiceClient for file operations.

        Args:
            account_name: Storage account name
            account_key: Storage account key

        Returns:
            ShareServiceClient object
        """
        return ShareServiceClient(
            account_url=f"https://{account_name}.file.{self.storage_suffix}",
            credential=account_key,
            connection_verify=False
        )


class FileShareCopier:
    """Handles file share copying operations."""

    def __init__(self, source_service_client: ShareServiceClient,
                 dest_service_client: ShareServiceClient):
        """
        Initialize file share copier.

        Args:
            source_service_client: Source ShareServiceClient
            dest_service_client: Destination ShareServiceClient
        """
        self.source_service_client = source_service_client
        self.dest_service_client = dest_service_client
        self.successful_count = 0
        self.failed_count = 0

    def calculate_total_size(self, share_name: str) -> Tuple[int, int]:
        """
        Calculate total size and count of all files in a file share.

        Args:
            share_name: File share name

        Returns:
            Tuple of (total_size_bytes, file_count)
        """
        total_size = 0
        file_count = 0

        share_client = self.source_service_client.get_share_client(share_name)

        def traverse_directory(directory_client: ShareDirectoryClient, path: str = ""):
            nonlocal total_size, file_count

            try:
                items = directory_client.list_directories_and_files()
                for item in items:
                    item_path = f"{path}/{item['name']}" if path else item['name']

                    if item['is_directory']:
                        subdir_client = share_client.get_directory_client(item_path)
                        traverse_directory(subdir_client, item_path)
                    else:
                        file_client = share_client.get_file_client(item_path)
                        properties = file_client.get_file_properties()
                        total_size += properties.size
                        file_count += 1
            except Exception as e:
                print(f"Error traversing directory {path}: {str(e)}")

        root_dir_client = share_client.get_directory_client("")
        traverse_directory(root_dir_client)

        return total_size, file_count

    def copy_file_with_verification(self, source_file_client: ShareFileClient,
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

    def copy_files_recursive(self, source_share_client, dest_share_client,
                            source_path: str = "", dest_path: str = "") -> Tuple[int, int]:
        """
        Recursively copy all files from source to destination.

        Args:
            source_share_client: Source share client
            dest_share_client: Destination share client
            source_path: Source path (relative)
            dest_path: Destination path (relative)

        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0

        # Get directory clients
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
                    # Create directory in destination
                    try:
                        dest_dir_client = dest_share_client.get_directory_client(dest_item_path)
                        dest_dir_client.create_directory()
                        print(f"Created directory: {dest_item_path}")
                    except (HttpResponseError, ResourceNotFoundError, Exception) as e:
                        if 'ResourceAlreadyExists' in str(e) or 'already exists' in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 409):
                            print(f"Directory already exists: {dest_item_path}")
                        else:
                            print(f"Warning: Error creating directory {dest_item_path}: {str(e)}")

                    # Recursively copy subdirectory
                    sub_success, sub_failed = self.copy_files_recursive(
                        source_share_client, dest_share_client,
                        source_item_path, dest_item_path
                    )
                    successful += sub_success
                    failed += sub_failed
                else:
                    # Copy file
                    source_file_client = source_share_client.get_file_client(source_item_path)
                    dest_file_client = dest_share_client.get_file_client(dest_item_path)

                    if self.copy_file_with_verification(source_file_client, dest_file_client, source_item_path):
                        successful += 1
                    else:
                        failed += 1

        except Exception as e:
            print(f"Error processing directory {source_path}: {str(e)}")
            if 'ResourceAlreadyExists' not in str(e) and 'already exists' not in str(e).lower():
                failed += 1

        return successful, failed

    def copy_share(self, source_share_name: str, dest_share_name: str,
                   dest_root_dir: str = None) -> Tuple[int, int]:
        """
        Copy entire file share from source to destination.

        Args:
            source_share_name: Source share name
            dest_share_name: Destination share name
            dest_root_dir: Optional root directory in destination

        Returns:
            Tuple of (successful_count, failed_count)
        """
        source_share_client = self.source_service_client.get_share_client(source_share_name)
        dest_share_client = self.dest_service_client.get_share_client(dest_share_name)

        # Create destination root directory if specified
        if dest_root_dir:
            dest_root_dir_client = dest_share_client.get_directory_client(dest_root_dir)
            try:
                dest_root_dir_client.create_directory()
                print(f"Created root directory in destination: {dest_root_dir}")
            except (ResourceNotFoundError, Exception) as e:
                if 'ResourceAlreadyExists' not in str(e):
                    print(f"Error creating root directory in destination: {str(e)}")
                    raise

        return self.copy_files_recursive(
            source_share_client, dest_share_client,
            source_path="", dest_path=dest_root_dir or ""
        )
