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

# find the download button with class "btn_vert" that contains "Installer edition"
# example: <a class="btn_vert" href="https://download.mobatek.net/2542025111600034/MobaXterm_Installer_v25.4.zip">
installer_url = None
version = None

# find all buttons with class "btn_vert"
buttons = soup.find_all('a', class_='btn_vert')

for button in buttons:
    href = button.get('href', '')
    text = button.get_text(strip=True)

    # look for installer edition
    if 'Installer edition' in text and 'MobaXterm_Installer_' in href:
        installer_url = href
        # extract version from text like "MobaXterm Home Edition v25.4(Installer edition)"
        # or from URL like "MobaXterm_Installer_v25.4.zip"
        version_match = re.search(r'v(\d+\.\d+)', text)
        if not version_match:
            version_match = re.search(r'v(\d+\.\d+)', href)
        if version_match:
            version = version_match.group(1)

if version and installer_url:
    print(f"Latest Version: {version}")
    print(f"Installer URL: {installer_url}")

else:
    print("Could not find version or download URL")
    if not version:
        print("  Missing: Version")
    if not installer_url:
        print("  Missing: Installer URL")

