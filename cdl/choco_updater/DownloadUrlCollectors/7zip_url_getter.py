import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT; Win64; x64)'}
url = 'https://7-zip.org/download.html'

# fetch the page
response = requests.get(url, headers=headers, verify=False)
response.raise_for_status()  # Ensure request was successful

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find the latest version from the first download link text
version = None
for element in soup.find_all('a', href=True):
    if '7z' in element['href'] and element['href'].endswith('.exe'):
        # Extract version from href like 'a/7z2501.exe'
        version = element['href'].split('/')[-1].replace('7z', '').replace('.exe', '')
        if 'x64' in version:
            # using walrus operator to split and reformat version, e.g., '2501-x64' -> '25.01'
            version = (v := version.split('-')[0])[:2] + '.' + v[2:]
        break

# collect URLs
urls = [f"https://www.7-zip.org/{a['href']}" for a in soup.find_all('a', href=True) if a['href'].endswith('.exe')]
url32 = next((u for u in urls if 'x64' not in u), None)
url64 = next((u for u in urls if 'x64' in u), None)

print(f"Latest Version: {version}")
print(f"32-bit URL: {url32}")
print(f"64-bit URL: {url64}")
