import requests
from bs4 import BeautifulSoup
import warnings
import re
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://dotnet.microsoft.com/en-us/download/dotnet'

print("Fetching page...")
resp = requests.get(url, headers=headers, verify=False, timeout=10)
print(f"Status: {resp.status_code}")
print(f"Content length: {len(resp.text)}")

soup = BeautifulSoup(resp.text, 'html.parser')

# Look for version links
print("\n=== Looking for version links ===")
version_links = soup.find_all('a', href=re.compile(r'/download/dotnet/\d+\.\d+'))
print(f"Found {len(version_links)} version links")

for i, link in enumerate(version_links[:5]):
    print(f"\n{i+1}. {link.get_text(strip=True)}")
    print(f"   href: {link.get('href')}")

# Look for div with id
print("\n=== Looking for supported-versions-table div ===")
div = soup.find('div', id='supported-versions-table')
print(f"Div found: {div is not None}")

if div:
    table = div.find('table')
    print(f"Table in div: {table is not None}")

