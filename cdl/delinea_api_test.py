#!/usr/bin/env python3
"""
Script to authenticate and retrieve secrets from Delinea Secret Server Cloud

tsvetelin.maslarski-ext@ldc.com
"""
import requests
import json
import sys
from urllib.parse import urljoin

class DelineaSecretServer:
    def __init__(self, base_url, username=None, password=None, token=None):
        """
        Initialize Delinea Secret Server client

        Args:
            base_url: Base URL (e.g., 'https://ldc.secretservercloud.eu')
            username: Username for authentication
            password: Password for authentication
            token: API token (if using token-based auth instead of username/password)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def authenticate(self):
        """Authenticate and get access token"""
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            print("Using provided API token")
            return True

        auth_url = f"{self.base_url}/oauth2/token"

        payload = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
        }

        try:
            print(f"Authenticating to {auth_url}...")
            response = self.session.post(auth_url, data=payload)
            response.raise_for_status()

            data = response.json()
            access_token = data.get('access_token')

            if access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
                print("Authentication successful!")
                return True
            else:
                print("No access token received")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return False

    def get_secret(self, secret_id):
        """
        Get secret by ID

        Args:
            secret_id: The secret ID to retrieve

        Returns:
            dict: Secret data
        """
        url = f"{self.api_base}/secrets/{secret_id}"

        try:
            print(f"Retrieving secret {secret_id}...")
            response = self.session.get(url)
            response.raise_for_status()

            secret_data = response.json()
            print("Secret retrieved successfully!")
            return secret_data

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve secret: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None

    def get_secret_field(self, secret_id, field_name):
        """
        Get specific field from a secret

        Args:
            secret_id: The secret ID
            field_name: Field name to retrieve (e.g., 'username', 'password')

        Returns:
            str: Field value
        """
        secret = self.get_secret(secret_id)
        if not secret:
            return None

        items = secret.get('items', [])
        for item in items:
            if item.get('slug') == field_name or item.get('fieldName') == field_name:
                return item.get('itemValue')

        print(f"Field '{field_name}' not found in secret")
        return None

    def search_secrets(self, search_text=None, folder_id=None):
        """
        Search for secrets

        Args:
            search_text: Text to search for
            folder_id: Folder ID to search in

        Returns:
            list: List of secrets
        """
        url = f"{self.api_base}/secrets"
        params = {}

        if search_text:
            params['filter.searchText'] = search_text
        if folder_id:
            params['filter.folderId'] = folder_id

        try:
            print(f"Searching secrets...")
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get('records', [])
            print(f"Found {len(records)} secret(s)")
            return records

        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []


def main():
    BASE_URL = "https://ldc.secretservercloud.eu"

    print("=" * 60)
    print("Delinea Secret Server Cloud API Test")
    print("=" * 60)
    print()

    # Get credentials
    print("Authentication options:")
    print("1. Username/Password")
    print("2. API Token")
    print()

    auth_method = input("Select authentication method (1 or 2): ").strip()

    if auth_method == "1":
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        client = DelineaSecretServer(BASE_URL, username=username, password=password)
    elif auth_method == "2":
        token = input("API Token: ").strip()
        client = DelineaSecretServer(BASE_URL, token=token)
    else:
        print("Invalid selection")
        return 1

    # Authenticate
    if not client.authenticate():
        print("\nAuthentication failed!")
        return 1

    print()
    print("=" * 60)
    print()

    # Main menu
    while True:
        print("\nOptions:")
        print("1. Get secret by ID")
        print("2. Get secret field by ID")
        print("3. Search secrets")
        print("4. Exit")
        print()

        choice = input("Select option: ").strip()

        if choice == "1":
            secret_id = input("Enter secret ID (e.g., 14023): ").strip()
            secret = client.get_secret(secret_id)
            if secret:
                print("\n" + "=" * 60)
                print(json.dumps(secret, indent=2))
                print("=" * 60)

        elif choice == "2":
            secret_id = input("Enter secret ID: ").strip()
            field_name = input("Enter field name (e.g., 'username', 'password'): ").strip()
            value = client.get_secret_field(secret_id, field_name)
            if value:
                print(f"\nField value: {value}")

        elif choice == "3":
            search_text = input("Enter search text (or leave empty): ").strip() or None
            secrets = client.search_secrets(search_text=search_text)
            if secrets:
                print("\n" + "=" * 60)
                for secret in secrets:
                    print(f"ID: {secret.get('id')} - {secret.get('name')}")
                print("=" * 60)

        elif choice == "4":
            break
        else:
            print("Invalid option")

    print("\nGoodbye and Good Night!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
