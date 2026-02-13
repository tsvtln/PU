import requests
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://slproweb.com/products/Win32OpenSSL.html'

response = requests.get(url, headers=headers, verify=False, timeout=30)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

# Save to file for inspection
with open('openssl_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Page saved to openssl_page.html")

# Look for exe mentions in the text
import re
exe_matches = re.findall(r'\S*Win(32|64)\S*Light\S*\.exe', response.text, re.IGNORECASE)
print(f"\nFound {len(exe_matches)} .exe matches:")
for match in exe_matches[:10]:
    print(f"  {match}")

