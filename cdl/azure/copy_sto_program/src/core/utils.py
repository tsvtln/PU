"""
Utility Functions Module
Common utility functions for the Azure file copy program.
"""

import hashlib
from typing import Dict


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_md5_from_bytes(data: bytes) -> str:
    """
    Calculate MD5 hash from bytes.

    Args:
        data: Bytes to hash

    Returns:
        MD5 hash as hex string
    """
    return hashlib.md5(data).hexdigest()


def check_storage_tiers(source_details: Dict[str, str],
                        dest_details: Dict[str, str]) -> bool:
    """
    Check if source is Premium and destination is Standard.

    Args:
        source_details: Source storage account details
        dest_details: Destination storage account details

    Returns:
        True if it's OK to continue
    """
    source_tier = source_details['sku_tier']
    dest_tier = dest_details['sku_tier']

    print(f"\nSource storage account: {source_details['name']}")
    print(f"  SKU: {source_details['sku_name']}, Tier: {source_tier}")

    print(f"\nDestination storage account: {dest_details['name']}")
    print(f"  SKU: {dest_details['sku_name']}, Tier: {dest_tier}")

    if source_tier == 'Premium' and dest_tier == 'Standard':
        print("\n✓ Source is Premium and destination is Standard - OK to continue")
        return True
    else:
        print(f"\n⚠ Warning: Source tier is '{source_tier}' and destination tier is '{dest_tier}' - Will not continue!")
        # response = input("Continue anyway? (yes/no): ")
        # return response.lower() in ['yes', 'y']
        return False


def check_quota(total_size: int, quota_bytes: int) -> bool:
    """
    Check if destination has enough quota.

    Args:
        total_size: Total size needed in bytes
        quota_bytes: Available quota in bytes

    Returns:
        True if OK to continue
    """
    if total_size > quota_bytes:
        print(f"\n⚠ WARNING: Source total size ({format_bytes(total_size)}) "
              f"exceeds destination quota ({format_bytes(quota_bytes)})")
        response = input("Continue anyway? (yes/no): ")
        return response.lower() in ['yes', 'y']
    return True


def setup_ssl_verification(disable: bool = True) -> None:
    """
    Setup SSL certificate verification settings.

    Args:
        disable: If True, disable SSL verification for corporate environments
    """
    if disable:
        import ssl
        import urllib3
        import warnings
        import os

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')

        # Set environment variables to disable SSL verification
        os.environ['AZURE_CLI_DISABLE_CONNECTION_VERIFICATION'] = '1'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['PYTHONHTTPSVERIFY'] = '0'

        # Create unverified SSL context
        ssl._create_default_https_context = ssl._create_unverified_context

