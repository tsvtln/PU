import requests
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://helpx.adobe.com/acrobat/release-note/release-notes-acrobat-reader.html'

# fetch the page
response = requests.get(url, headers=headers, verify=False)
response.raise_for_status()  # Ensure request was successful

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# pattern to match version like "24.001.20604"
version_pattern = re.compile(r'([0-9]{2}\.[0-9]{3}\.[0-9]{5,})')

# find the latest version from the page text
release = None
full_text = soup.get_text()
matches = version_pattern.findall(full_text)

if matches:
    release = matches[0]

if release:
    version = f"20{release}"
    release_folder = release.replace('.', '')

    # construct URLs
    exe_filename = f"AcroRdrDCx64{release_folder}_MUI.exe"
    exe_url = f"https://ardownload3.adobe.com/pub/adobe/acrobat/win/AcrobatDC/{release_folder}/{exe_filename}"
    msp_filename = f"AcroRdrDCx64Upd{release_folder}_MUI.msp"
    msp_url = f"https://ardownload3.adobe.com/pub/adobe/acrobat/win/AcrobatDC/{release_folder}/{msp_filename}"

    print(f"Latest Version: {version}")
    print(f"EXE URL: {exe_url}")
    print(f"MSP URL: {msp_url}")
else:
    print("Could not find version information")

