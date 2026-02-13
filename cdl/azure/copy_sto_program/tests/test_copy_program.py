"""
Unit Tests for Azure File Share Copy Program
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import hashlib
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from src.core.utils import format_bytes, calculate_md5_from_bytes, check_storage_tiers
from src.config.settings import StorageAccountConfig, CopyConfig, EnvironmentConfig


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_format_bytes(self):
        """Test byte formatting."""
        self.assertEqual(format_bytes(0), "0.00 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1048576), "1.00 MB")
        self.assertEqual(format_bytes(1073741824), "1.00 GB")

    def test_calculate_md5_from_bytes(self):
        """Test MD5 calculation."""
        test_data = b"Hello, World!"
        expected_md5 = hashlib.md5(test_data).hexdigest()
        self.assertEqual(calculate_md5_from_bytes(test_data), expected_md5)

    @patch('builtins.input', return_value='yes')
    def test_check_storage_tiers_premium_to_standard(self, mock_input):
        """Test storage tier check for Premium to Standard."""
        source = {'name': 'src', 'sku_name': 'Premium_LRS', 'sku_tier': 'Premium'}
        dest = {'name': 'dst', 'sku_name': 'Standard_LRS', 'sku_tier': 'Standard'}
        self.assertTrue(check_storage_tiers(source, dest))


class TestConfig(unittest.TestCase):
    """Test configuration classes."""

    def test_storage_account_config(self):
        """Test StorageAccountConfig creation."""
        config = StorageAccountConfig(
            storage_account='testaccount',
            resource_group='testrg',
            share_name='testshare'
        )
        self.assertEqual(config.storage_account, 'testaccount')
        self.assertEqual(config.resource_group, 'testrg')
        self.assertEqual(config.share_name, 'testshare')

    def test_copy_config_validation(self):
        """Test CopyConfig validation."""
        source = StorageAccountConfig(storage_account='src', share_name='srcshare')
        dest = StorageAccountConfig(storage_account='dst', share_name='dstshare')

        # Valid config
        config = CopyConfig(source=source, destination=dest, environment='global')
        self.assertEqual(config.environment, 'global')

        # Invalid environment
        with self.assertRaises(ValueError):
            CopyConfig(source=source, destination=dest, environment='invalid')

    def test_environment_config(self):
        """Test environment configuration."""
        global_config = EnvironmentConfig.get_config('global')
        self.assertIsNone(global_config['base_url'])
        self.assertEqual(global_config['storage_suffix'], 'core.windows.net')

        china_config = EnvironmentConfig.get_config('china')
        self.assertEqual(china_config['base_url'], 'https://management.chinacloudapi.cn')
        self.assertEqual(china_config['storage_suffix'], 'core.chinacloudapi.cn')


class TestAzureAuth(unittest.TestCase):
    """Test Azure authentication module."""

    @patch('azure_auth.load_dotenv')
    @patch('azure_auth.os.getenv')
    def test_load_credentials_global(self, mock_getenv, mock_load_dotenv):
        """Test loading credentials for global environment."""
        from azure_auth import AzureAuthenticator

        mock_getenv.side_effect = lambda key: {
            'tenant_id': 'test-tenant',
            'client_id': 'test-client',
            'client_secret': 'test-secret'
        }.get(key)

        auth = AzureAuthenticator(environment='global', use_decouple=False)
        auth.load_env_file(Path(__file__).parent / 'test.env')

        tenant_id, client_id, client_secret = auth.load_credentials()
        self.assertEqual(tenant_id, 'test-tenant')
        self.assertEqual(client_id, 'test-client')
        self.assertEqual(client_secret, 'test-secret')


if __name__ == '__main__':
    unittest.main()
