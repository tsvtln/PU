import requests
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Test the URL pattern
test_url = "https://www.voidtools.com/Everything-1.4.1.1030.x64-Setup.exe"
print(f"Testing URL: {test_url}")

try:
    response = requests.head(test_url, headers=headers, verify=False, timeout=10, allow_redirects=True)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")

    if response.status_code == 200:
        print("URL is valid!")
    else:
        print("URL might not be valid")
except Exception as e:
    print(f"Error: {e}")

