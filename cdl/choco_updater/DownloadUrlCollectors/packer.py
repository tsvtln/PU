import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
online_domain = 'https://releases.hashicorp.com'
releases = f'{online_domain}/packer/'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find links matching pattern /packer/. (any character after /packer/)
# look for links like /packer/1.14.3/
pattern = re.compile(r'/packer/.')
url = None

for link in soup.find_all('a', href=True):
    href = link['href']
    if pattern.search(href):
        url = online_domain + href
        break

if url:
    # extract version from URL
    # split by '/' and skip 4, take first 1
    # example: https://releases.hashicorp.com/packer/1.11.2/ -> ['https:', '', 'releases.hashicorp.com', 'packer', '1.11.2', '']
    # skip 4 gets us to index 4, which is '1.11.2'
    parts = url.split('/')
    version = parts[4] if len(parts) > 4 else None

    if version:
        # construct download URLs
        url64 = f"{url}packer_{version}_windows_amd64.zip"
        url32 = f"{url}packer_{version}_windows_386.zip"

        print(f"Latest Version: {version}")
        print(f"32-bit URL: {url32}")
        print(f"64-bit URL: {url64}")
    else:
        print("Could not extract version from URL")
else:
    print("Could not find packer release URL")

