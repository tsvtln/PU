import requests
import os
from getpass import getpass
from decouple import config
import urllib3 as u3l
u3l.disable_warnings()

AWX_URL = "https://atwctl.d1.ad.local"
INVENTORY_ID = "19"

USERNAME = config('USR')
PASSWORD = config('PASS')

def get_auth_headers():
    headers = {"Content-Type": "application/json"}
    return headers, (USERNAME, PASSWORD)


def query_hosts():
    url = f"{AWX_URL}/api/v2/inventories/{INVENTORY_ID}/hosts/"
    all_hosts = []
    total_count = 0

    try:
        auth_result = get_auth_headers()
        headers, auth = auth_result

        # Handle pagination - keep fetching until there's no 'next' page
        while url:
            response = requests.get(url, headers=headers, auth=auth, verify=False)
            response.raise_for_status()

            data = response.json()

            # Get total count from first page
            if total_count == 0:
                total_count = data.get('count', 0)

            # Add hosts from this page to our list
            all_hosts.extend(data.get('results', []))

            # Get the next page URL, or None if this is the last page
            next_url = data.get('next')

            # If next_url is a relative path, prepend the base URL
            if next_url and next_url.startswith('/'):
                url = f"{AWX_URL}{next_url}"
            else:
                url = next_url

        # Now print all hosts we collected
        print(f"Found {total_count} hosts:")
        for host in all_hosts:
            print(f"- {host.get('name')} (ID: {host.get('id')})")

        # Search for specific host
        print("\nSearching for CSM1KPOCVMW927...")
        for host in all_hosts:
            if 'CSM1KPOCVMW927' in host.get('name'):
                print(f"Found host: {host.get('name')} with ID {host.get('id')}")

        return all_hosts

    except requests.exceptions.RequestException as e:
        print(f"Error querying AWX API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None

if __name__ == "__main__":
    query_hosts()
