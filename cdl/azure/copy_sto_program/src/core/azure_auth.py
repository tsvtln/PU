"""
Azure Authentication Module
Handles Azure authentication using Service Principal credentials.
"""

import os
import sys
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from decouple import config


class AzureAuthenticator:
    """Handles Azure authentication for different environments."""

    def __init__(self, environment: str = 'global', use_decouple: bool = False):
        """
        Initialize the authenticator.

        Args:
            environment: 'global' or 'china'
            use_decouple: Use python-decouple config() instead of os.getenv()
        """
        self.environment = environment
        self.use_decouple = use_decouple
        self.credential = None

    def load_env_file(self, env_path: Path = None) -> None:
        """Load .env file from specified path or script directory."""
        if env_path is None:
            script_dir = Path(__file__).parent.parent
            env_path = script_dir / '.env'

        if not env_path.exists():
            raise FileNotFoundError(f".env file not found at {env_path}")

        load_dotenv(env_path)

    def load_credentials(self) -> Tuple[str, str, str]:
        """
        Load credentials from environment based on environment type.

        Returns:
            Tuple of (tenant_id, client_id, client_secret)
        """
        if self.environment == 'china':
            suffix = '_china'
        else:
            suffix = ''

        if self.use_decouple:
            tenant_id = config(f'tenant_id{suffix}')
            client_id = config(f'client_id{suffix}')
            client_secret = config(f'client_secret{suffix}')
        else:
            tenant_id = os.getenv(f'tenant_id{suffix}')
            client_id = os.getenv(f'client_id{suffix}')
            client_secret = os.getenv(f'client_secret{suffix}')

            # Remove quotes if present
            if tenant_id:
                tenant_id = tenant_id.strip('"')
            if client_id:
                client_id = client_id.strip('"')
            if client_secret:
                client_secret = client_secret.strip('"')

        if not tenant_id or not client_id or not client_secret:
            env_name = 'China' if self.environment == 'china' else 'Global'
            raise ValueError(
                f"Missing credentials for {env_name} environment in .env file. "
                f"Required: tenant_id{suffix}, client_id{suffix}, client_secret{suffix}"
            )

        return tenant_id, client_id, client_secret

    def authenticate(self) -> ClientSecretCredential:
        """
        Authenticate and return credential object.

        Returns:
            ClientSecretCredential object
        """
        tenant_id, client_id, client_secret = self.load_credentials()

        if self.environment == 'china':
            authority = 'https://login.chinacloudapi.cn'
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                authority=authority
            )
        else:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )

        return self.credential

    def get_credential(self) -> ClientSecretCredential:
        """Get or create credential."""
        if self.credential is None:
            self.authenticate()
        return self.credential

