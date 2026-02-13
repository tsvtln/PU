import requests
from decouple import config

AWX_URL = "https://atwctl.d1.ad.local"
USERNAME = config('USR')
PASSWORD = config('PASS')

def get_auth_headers():
    headers = {"Content-Type": "application/json"}
    return headers, (USERNAME, PASSWORD)

def list_inventories():
    url = f"{AWX_URL}/api/v2/inventories/"
    try:
        headers, auth = get_auth_headers()
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        response.raise_for_status()
        data = response.json()
        print(f"Found {data.get('count', 0)} inventories:")
        for inv in data.get('results', []):
            print(f"- {inv.get('name')} (ID: {inv.get('id')})")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error querying AWX API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None

if __name__ == "__main__":
    list_inventories()

