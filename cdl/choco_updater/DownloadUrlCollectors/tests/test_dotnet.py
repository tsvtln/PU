import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://dotnet.microsoft.com/en-us/download/dotnet'

print("Fetching page...")
resp = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(resp.text, 'html.parser')

print("\n=== Looking for table ===")
table = soup.find('table', attrs={'aria-labelledby': 'dotnetcore-version'})
print(f"Table found: {table is not None}")

if table:
    print("\n=== Table structure ===")
    tbody = table.find('tbody')
    print(f"Has tbody: {tbody is not None}")
    
    print("\n=== All rows in table ===")
    rows = table.find_all('tr', recursive=True)
    print(f"Total rows: {len(rows)}")
    
    for i, row in enumerate(rows[:5]):  # Show first 5 rows
        print(f"\nRow {i}:")
        link = row.find('a', href=True)
        if link:
            print(f"  Link text: {link.get_text(strip=True)}")
            print(f"  Link href: {link.get('href')}")
        else:
            print(f"  No link found")
            print(f"  Row text: {row.get_text(strip=True)[:100]}")

