import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
download_page = 'https://www.citrix.com/downloads/workspace-app/workspace-app-for-windows-long-term-service-release/workspace-app-for-windows-LTSR-Latest.html'
response = ''
try:
    # fetch the page
    for i in range(2):  # Retry twice, because the first time we cache a qda
        response = requests.get(download_page, headers=headers, verify=False, timeout=30)
    response.raise_for_status()

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = response.text

    version = None
    url64 = None

    # Find version in format 24.2.4001.1
    # This is the actual version number used by Citrix
    version_pattern = re.compile(r'\b(\d{2}\.\d+\.\d{4}\.\d+)\b')
    version_matches = version_pattern.findall(page_text)

    if version_matches:
        # Get the first (should be the latest) version
        version = version_matches[0]

    # Find the base download URL
    # Pattern: https://downloads.citrix.com/{rel_id}/CitrixWorkspaceFullInstaller.exe
    base_url_pattern = re.compile(r'(https://downloads\.citrix\.com/\d+/CitrixWorkspaceFullInstaller\.exe)')
    base_url_match = base_url_pattern.search(page_text)

    if base_url_match:
        base_url = base_url_match.group(1)

        # Find the __gda__ parameters
        gda_pattern = re.compile(r'(__gda__=exp=\d+~acl=/\*~hmac=[a-f0-9]+)')
        gda_match = gda_pattern.search(page_text)

        if gda_match:
            gda_params = gda_match.group(1)
            # Construct full URL with query parameters
            url64 = f"{base_url}?{gda_params}"
        else:
            # If no __gda__ params found, use base URL (may not work without manual download)
            url64 = base_url

    if version and url64:
        print(f"Latest Version: {version}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not find Citrix Workspace version or download URL")
        if not version:
            print("  Missing: version")
        if not url64:
            print("  Missing: 64-bit URL")

except requests.RequestException as e:
    print(f"Could not fetch Citrix Workspace version: {e}")
except Exception as e:
    print(f"Error processing Citrix Workspace version: {e}")

