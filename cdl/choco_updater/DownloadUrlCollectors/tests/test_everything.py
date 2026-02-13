import requests
import re
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.voidtools.com/Changes.txt'

print("Fetching Changes.txt...")
response = requests.get(url, headers=headers, verify=False, timeout=30)
print(f"Status: {response.status_code}")

# Get first 50 lines to see format
lines = response.text.split('\n')
print(f"\nTotal lines: {len(lines)}")
print("\nFirst 20 lines:")
for i, line in enumerate(lines[:20]):
    print(f"{i}: {repr(line)}")

# Look for version pattern
print("\n=== Looking for version pattern ===")
version_pattern = re.compile(r': Version .+')
for i, line in enumerate(lines[:30]):
    if version_pattern.search(line):
        print(f"Found at line {i}: {line}")
        # Extract version
        parts = line.split()
        print(f"Parts: {parts}")
        if len(parts) > 0:
            version = parts[-1].strip()
            print(f"Version: {version}")
        break

