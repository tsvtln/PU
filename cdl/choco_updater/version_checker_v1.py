"""
This program will clone each repo from the AZURE_REPOS list, find .nuspec files.
Afterwards it's going to parse the <version> tag in the nuspec file to get the local version.
Finally it will query the official Chocolatey API for the latest version and will compare and report outdated packages.

"""

import os
import requests
import subprocess
import urllib3 as u3l
u3l.disable_warnings()
import xml.etree.ElementTree as ET
import packaging.version



# array for all ADO repos to check. Adding them here manually, can possibly try to figure out later
# if we can automatically scan all repos in some way
AZURE_REPOS = [
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/googlechrome",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/7zip",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/adobereader",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/agentransack",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/azcopy10",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/azure-cli",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/azure-pipelines-agent",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/bginfo",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/checksum",
    # good above
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/curl",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/delprof2",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/dotNet",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/dotnetcore-sdk",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/dotnetfx",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/git",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/hp-universal-print-driver-pcl-master",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/microsoft-defender-platform",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/microsoft-monitoring-agent",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/microsoftazurestorageexplorer",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/nodejs",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/notepadplusplus",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/office2016",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/office2021",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/opconAgent",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/opconsqlagent",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/openssl",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/packer",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/pandoc",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/podman",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/podman-desktop",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/proget_maintenance",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/putty",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/pycharm-community",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/python3",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/qgis",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/sap-gui",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/scripts",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/setdefaultbrowser",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/solarwinds-agent",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/sql2012.nativeclient",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/sqlserver-odbcdriver",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/ssms19",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/sysinternals",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/terraform",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/uipathremoteruntime",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/vcredist2005",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/vcredist2008",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/vcredist2013",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/velero",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/visualstudio2019professional",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/visualstudio2022professional",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/vscode",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/webdeploy",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/winmerge",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/winscp",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/yarn",
    # "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/yml.pipeline",
]

not_in_public_repo = [
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/cisassessor",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/citrixPowerShell",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/citrixstorefront",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/citrixvda",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/citrixwemagent",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/citrixworkspace",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/dotnetfx35",
    "https://LDC-Technology-and-Operations@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/Ghostscript",

]

def get_nuspec_info(nuspec_path):
    # try namespace-aware parsing first
    try:
        tree = ET.parse(nuspec_path)
        root = tree.getroot()
        ns = {'ns': 'http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd'}
        version = root.find('.//ns:version', ns)
        package_id = root.find('.//ns:id', ns)
        if package_id is not None and version is not None:
            return package_id.text, version.text
    except Exception:
        pass
    # fallback to try without namespace
    try:
        tree = ET.parse(nuspec_path)
        root = tree.getroot()
        version = root.find('.//version')
        package_id = root.find('.//id')
        if package_id is not None and version is not None:
            return package_id.text, version.text
    except Exception:
        pass
    # fallback to try to extract from file name or repo name
    package_id = os.path.splitext(os.path.basename(nuspec_path))[0]
    version = None
    # try to extract version from file as plain text
    try:
        with open(nuspec_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '<version>' in line:
                    version = line.split('<version>')[1].split('</version>')[0].strip()
                    break
    except Exception:
        pass
    return (package_id, version)

def get_latest_choco_version(package_id):
    # print(f"Querying Chocolatey API for package_id: {package_id}")
    # Use FindPackagesById endpoint for reliable results
    url = f"https://community.chocolatey.org/api/v2/FindPackagesById()?id='{package_id.lower()}'"
    resp = requests.get(url, verify=False)
    versions = []
    if resp.status_code == 200:
        tree = ET.fromstring(resp.content)
        # Find all <d:Version> tags
        for ver in tree.findall('.//{http://schemas.microsoft.com/ado/2007/08/dataservices}Version'):
            if ver is not None and ver.text:
                if 'rtw' in ver.text:
                    ver_redacted = ver.text.replace('-rtw', '')
                    versions.append(ver_redacted)
                elif 'prerelease' in ver.text:
                    ver_redacted = ver.text.replace('-prerelease', '')
                    versions.append(ver_redacted)
                else:
                    versions.append(ver.text)
        # print(f"Versions extracted: {versions}")
        if versions:
            return sorted(versions, key=packaging.version.parse)[-1]
    else:
        print(f"API request failed for package_id: {package_id} with status code {resp.status_code}")
    return None

def main():
    outdated = []
    for repo_url in AZURE_REPOS:
        repo_name = repo_url.split('/')[-1]
        if not os.path.exists(repo_name):
            subprocess.run(
                ["git", "clone", repo_url, repo_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        for root, dirs, files in os.walk(repo_name):
            for file in files:
                if file.endswith(".nuspec"):
                    nuspec_path = os.path.join(root, file)
                    package_id, local_version = get_nuspec_info(nuspec_path)
                    latest_version = get_latest_choco_version(package_id)
                    if local_version and latest_version and local_version != latest_version:
                        outdated.append((package_id, local_version, latest_version))
                        print(f"{package_id}: local={local_version}, latest={latest_version} [OUTDATED]")
                    else:
                        print(f"{package_id}: local={local_version}, latest={latest_version} [OK]")
        # clean up cloned repos after checks
        if os.path.exists(repo_name):
            try:
                if os.name == 'nt':
                    subprocess.run(["rmdir", "/S", "/Q", repo_name], shell=True)
                else:
                    subprocess.run(["rm", "-rf", repo_name])
            except Exception as e:
                print(f"Failed to remove {repo_name}: {e}")

        print(outdated)

if __name__ == "__main__":
    main()
