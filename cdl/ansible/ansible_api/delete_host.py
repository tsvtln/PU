import requests
from decouple import config

AWX_URL = "https://atwctl.d1.ad.local"
USERNAME = config('USR')
PASSWORD = config('PASS')

def get_auth_headers():
    headers = {"Content-Type": "application/json"}
    return headers, (USERNAME, PASSWORD)

def delete_host_by_id(host_id):
    url = f"{AWX_URL}/api/v2/hosts/{host_id}/"
    try:
        headers, auth = get_auth_headers()
        response = requests.delete(url, headers=headers, auth=auth, verify=False)
        if response.status_code == 204:
            print(f"Host with ID {host_id} deleted successfully.")
        else:
            print(f"Failed to delete host with ID {host_id}. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting host: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    delete_host_by_id(100)