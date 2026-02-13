import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
download_page = 'https://mobaxterm.mobatek.net/download-home-edition.html'

# fetch the page
response = requests.get(download_page, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find the download button with class 'btn_vert' that contains 'Installer edition'
# pattern: MobaXterm_Installer_v{version}.zip
installer_url = None
version = None

for link in soup.find_all('a', class_='btn_vert', href=True):
    href = link['href']
    text = link.get_text(strip=True)

    # look for Installer edition
    if 'Installer edition' in text and 'MobaXterm_Installer' in href:
        installer_url = href
        # extract version from the button text
        # example: "MobaXterm Home Edition v25.4(Installer edition)"
        version_match = re.search(r'v(\d+\.\d+)', text)
        if version_match:
            version = version_match.group(1)


if installer_url and version:
    print(f"Latest Version: {version}")
    print(f"Installer URL: {installer_url}")
else:
    print("Could not find MobaXterm download URL or version")
    if not version:
        print("  Missing: version")
    if not installer_url:
        print("  Missing: Installer URL")
