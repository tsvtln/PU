import requests
import json
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== Testing local JSON hashes ===")
try:
    r = requests.get('https://slproweb.com/download/win32_openssl_hashes.json',
                     headers=headers, verify=False, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"JSON has 'files' key: {'files' in data}")
        if 'files' in data:
            files = data['files']
            print(f"Number of files: {len(files)}")
            # Show first few Light installer entries
            light_count = 0
            for filename, fileinfo in files.items():
                if fileinfo.get('light') == True and fileinfo.get('installer') == 'exe':
                    print(f"\nLight installer: {filename}")
                    print(f"  arch: {fileinfo.get('arch')}, bits: {fileinfo.get('bits')}")
                    print(f"  version: {fileinfo.get('basever')}{fileinfo.get('subver')}")
                    print(f"  url: {fileinfo.get('url')}")
                    light_count += 1
                    if light_count >= 4:
                        break
except Exception as e:
    print(f"Error: {e}")



