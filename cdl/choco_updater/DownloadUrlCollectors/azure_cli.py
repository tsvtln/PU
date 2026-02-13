import requests
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://aka.ms/installazurecliwindows'

# fetch the page with redirects disabled to get the Location header
response = requests.get(url, headers=headers, allow_redirects=False, verify=False)

# get the redirect URL from Location header
download_url = response.headers.get('Location', '')

if download_url:
    # extract version from URL like: https://azcliprod.azureedge.net/msi/azure-cli-2.66.0.msi
    # split by '-' and '.msi', then get the version (last element before .msi)
    parts = download_url.replace('.msi', '').split('-')
    version = parts[-1]

    print(f"Latest Version: {version}")
    print(f"Download URL: {download_url}")
else:
    print("Could not find download URL")

