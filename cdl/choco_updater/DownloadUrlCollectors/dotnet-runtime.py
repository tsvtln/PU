import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

# set up headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
releases = 'https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core'

# fetch the page
response = requests.get(releases, headers=headers, verify=False)
response.raise_for_status()

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# find the table with supported versions
# Looking for table with aria-labelledby="supported-versions" or id="supported-versions"
table = soup.find('table', {'aria-labelledby': 'supported-versions'})

if not table:
    # Try alternative ways to find the table
    table = soup.find('table', class_='table')

if table:
    # Find all rows in tbody
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        if rows:
            # Get the first row (latest version)
            first_row = rows[0]
            cells = first_row.find_all('td')

            if len(cells) >= 3:
                # The "Latest patch version" is in the 3rd column (index 2)
                version = cells[2].text.strip()

                # Build download URLs
                url32 = f"https://builds.dotnet.microsoft.com/dotnet/Runtime/{version}/dotnet-runtime-{version}-win-x86.exe"
                url64 = f"https://builds.dotnet.microsoft.com/dotnet/Runtime/{version}/dotnet-runtime-{version}-win-x64.exe"

                print(f"Latest Version: {version}")
                print(f"32-bit URL: {url32}")
                print(f"64-bit URL: {url64}")
            else:
                print("Could not find enough columns in the table row")
        else:
            print("No rows found in table body")
    else:
        print("No tbody found in table")
else:
    print("Could not find the supported versions table")

