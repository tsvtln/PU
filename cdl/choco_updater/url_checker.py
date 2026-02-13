import requests
import urllib3 as u3l
u3l.disable_warnings()

# URLS = [
#     "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/googlechrome",
#     "https://community.chocolatey.org/api/v2/FindPackagesById()?id='googlechrome'",
#     "http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd",
#     "http://schemas.microsoft.com/ado/2007/08/dataservices",
#     "https://dl.google.com/chrome/install/googlechromestandaloneenterprise64.msi",
#     "https://dl.google.com/chrome/install/googlechromestandaloneenterprise.msi",
#     "https://cdn.jsdelivr.net/gh/chocolatey-community/chocolatey-packages@edba4a5849ff756e767cba86641bea97ff5721fe/icons/chrome.svg",
#     "https://github.com/chocolatey-community/chocolatey-packages/tree/master/automatic/googlechrome",
#     "https://chocoinstall.ldc.com/Packages/googlechrome/140.0.7339.186/googlechromestandaloneenterprise64.msi",
#     "https://chocoinstall.ldc.com/Packages/googlechrome/140.0.7339.186/googlechromestandaloneenterprise.msi",
#     "https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_apis/git/repositories/googlechrome/pullrequests?api-version=7.0"
# ]

URLS = [
    "https://LDC-Technology-and-Operations@dev.azure.com",
    "https://community.chocolatey.org",
    "http://schemas.microsoft.com",
    "https://dl.google.com/",
    "https://cdn.jsdelivr.net/",
    "https://github.com/",
    "https://api.github.com/",
    "https://chocoinstall.ldc.com/",
    "https://dev.azure.com/",
    "https://7-zip.org/",
    "https://ardownload2.adobe.com/pub/adobe/reader/win/AcrobatDC/2500120997/AcroRdrDC2500120997_MUI.exe",
    "https://ardownload3.adobe.com/pub/adobe/acrobat/win/AcrobatDC/2500120997/AcroRdrDCx64Upd2500120997_MUI.msp",
    "https://azcliprod.blob.core.windows.net/msi/azure-cli-2.81.0.msi",
    "https://download.agent.dev.azure.com/agent/4.264.2/pipelines-agent-win-x86-4.264.2.zip",
    "https://curl.se",
    "https://releases.hashicorp.com/",
    "https://the.earth.li",
    "https://www.python.org",
    "https://microsoft.com",
    "https://sourceforge.net",
    "https://mythicsoftdownload.s3.eu-west-1.amazonaws.com/",
    "https://www.mythicsoft.com",
    "https://amazonaws.com",
    "https://azcliprod.blob.core.windows.net/msi/azure-cli-2.81.0.msi",
    "https://windows.net/",
    "https://download.sysinternals.com/",
    "https://sysinternals.com/",
    "https://downloads.citrix.com/",
    "https://citrix.com/",
    "https://helgeklein.com/",
    "https://desktop.docker.com",
    "https://docker.com",
    "https://www.voidtools.com",
    "https://aka.ms/installazurecliwindows",
    "https://www.ghostscript.com",
    "https://nodejs.org/",
    "https://slproweb.com",
    "http://www.chiark.greenend.org.uk",
    "https://data.services.jetbrains.com/",
    "https://download.jetbrains.com",
    "https://qgis.org",
    'https://update.code.visualstudio.com/',
    "http://winmerge.org/",
    "https://winscp.net/",
]


def check_urls(urls):
    for url in urls:
        try:
            resp = requests.get(url, timeout=10, verify=False)
            if resp.status_code == 200:
                print(f"{url} OK")
            else:
                print(f"{url} NOK")
        except Exception:
            print(f"{url} NOK")

if __name__ == "__main__":
    check_urls(URLS)
