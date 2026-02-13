"""
Configuration Module
Handles program configuration and settings.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StorageAccountConfig:
    """Configuration for a storage account."""
    storage_account: str
    resource_group: Optional[str] = None
    subscription_id: Optional[str] = None
    share_name: str = ""


@dataclass
class CopyConfig:
    """Configuration for copy operation."""
    source: StorageAccountConfig
    destination: StorageAccountConfig
    environment: str = 'global'
    use_decouple: bool = False
    disable_ssl_verify: bool = True
    create_root_dir: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if self.environment not in ['global', 'china']:
            raise ValueError("Environment must be 'global' or 'china'")


class EnvironmentConfig:
    """Environment-specific configuration."""

    ENVIRONMENTS = {
        'global': {
            'base_url': None,
            'storage_suffix': 'core.windows.net',
            'authority': None
        },
        'china': {
            'base_url': 'https://management.chinacloudapi.cn',
            'storage_suffix': 'core.chinacloudapi.cn',
            'authority': 'https://login.chinacloudapi.cn'
        }
    }

    @classmethod
    def get_config(cls, environment: str) -> dict:
        """
        Get configuration for specified environment.

        Args:
            environment: 'global' or 'china'

        Returns:
            Dictionary with environment configuration
        """
        return cls.ENVIRONMENTS.get(environment, cls.ENVIRONMENTS['global'])

