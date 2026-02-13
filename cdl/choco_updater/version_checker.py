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
import base64
import hashlib
import re
import shutil
# for testing
from decouple import config



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

def update_nuspec_version(nuspec_path, new_version):
    tree = ET.parse(nuspec_path)
    root = tree.getroot()
    ns = {'ns': 'http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd'}
    version = root.find('.//ns:version', ns)
    if version is not None:
        version.text = new_version
    else:
        version = root.find('.//version')
        if version is not None:
            version.text = new_version
    tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)

def update_outdated_packages(outdated, ado_token, username):
    for pkg in outdated:
        package_id = pkg['package_id']
        if package_id.lower() == "googlechrome":
            update_googlechrome_package(pkg, ado_token, username)
        else:
            # Placeholder for other packages
            pass

def create_and_push_branch(repo_name, branch_name, username, ado_token):
    # Create branch
    subprocess.run([
        "git", "checkout", "-b", branch_name
    ], cwd=repo_name)
    # Add and commit all changes
    subprocess.run([
        "git", "add", "."
    ], cwd=repo_name)
    subprocess.run([
        "git", "commit", "-m", f"Update {repo_name} to version {branch_name.replace('update-to-', '')}"
    ], cwd=repo_name)
    # Push branch
    push_url = f"https://{username}:{ado_token}@dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/{repo_name}"
    subprocess.run([
        "git", "push", push_url, branch_name
    ], cwd=repo_name)


def create_pull_request(repo_name, branch_name, pkg, ado_token):
    org = "LDC-Technology-and-Operations"
    project = "WPM-Chocolatey"
    api_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_name}/pullrequests?api-version=7.0"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{ado_token}".encode()).decode(),
        "Content-Type": "application/json"
    }
    pr_data = {
        "sourceRefName": f"refs/heads/{branch_name}",
        "targetRefName": "refs/heads/master",
        "title": f"Update {pkg['package_id']} to {pkg['latest_version']}",
        "description": f"Automated update of {pkg['package_id']} from {pkg['local_version']} to {pkg['latest_version']}",
    }
    try:
        resp = requests.post(api_url, headers=headers, json=pr_data, verify=False)
        if resp.status_code == 201:
            print(f"PR created for {pkg['package_id']}.")
        else:
            print(f"Failed to create PR for {pkg['package_id']}: {resp.text}")
    except Exception as e:
        print(f"Exception creating PR for {pkg['package_id']}: {e}")


def update_googlechrome_nuspec(nuspec_path, new_version):
    tree = ET.parse(nuspec_path)
    root = tree.getroot()
    ns = {'ns': root.tag.split('}')[0].strip('{')}
    # Update <version>
    version_tag = root.find('.//ns:version', ns)
    if version_tag is not None:
        version_tag.text = new_version
    # Update <iconUrl>
    icon_tag = root.find('.//ns:iconUrl', ns)
    if icon_tag is not None:
        icon_tag.text = "https://cdn.jsdelivr.net/gh/chocolatey-community/chocolatey-packages@edba4a5849ff756e767cba86641bea97ff5721fe/icons/chrome.svg"
    # Update <packageSourceUrl>
    src_tag = root.find('.//ns:packageSourceUrl', ns)
    if src_tag is not None:
        src_tag.text = "https://github.com/chocolatey-community/chocolatey-packages/tree/master/automatic/googlechrome"
    tree.write(nuspec_path, encoding='utf-8', xml_declaration=True)

def download_and_save_chrome_installers(version, share_base, package_name):
    """
    Download official Google Chrome MSI installers and save to Azure file share.
    Returns the full paths to the saved MSI files.
    """
    # Official URLs
    url64 = "https://dl.google.com/chrome/install/googlechromestandaloneenterprise64.msi"
    url = "https://dl.google.com/chrome/install/googlechromestandaloneenterprise.msi"
    # Download installers to temp
    installer64_temp = f"googlechromestandaloneenterprise64_{version}.msi"
    installer_temp = f"googlechromestandaloneenterprise_{version}.msi"
    r64 = requests.get(url64, stream=True)
    r = requests.get(url, stream=True)
    with open(installer64_temp, 'wb') as f:
        for chunk in r64.iter_content(chunk_size=8192):
            f.write(chunk)
    with open(installer_temp, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    # Save to share
    target_dir = os.path.join(share_base, package_name, version)
    os.makedirs(target_dir, exist_ok=True)
    installer_path = os.path.join(target_dir, "googlechromestandaloneenterprise.msi")
    installer64_path = os.path.join(target_dir, "googlechromestandaloneenterprise64.msi")
    shutil.copy2(installer_temp, installer_path)
    shutil.copy2(installer64_temp, installer64_path)
    # Clean up temp files
    os.remove(installer_temp)
    os.remove(installer64_temp)
    return installer_path, installer64_path

def update_googlechrome_install_ps1(ps1_path, new_version, installer_path, installer64_path):
    # Read the file
    with open(ps1_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Extract checksum types
    checksum_type_match = re.search(r"checksumType\s*=\s*'([^']+)'", content)
    checksum_type64_match = re.search(r"checksumType64\s*=\s*'([^']+)'", content)
    checksum_type = checksum_type_match.group(1) if checksum_type_match else 'sha256'
    checksum_type64 = checksum_type64_match.group(1) if checksum_type64_match else 'sha256'
    # Calculate checksums from saved files
    checksum64 = calculate_checksum(installer64_path, checksum_type64)
    checksum = calculate_checksum(installer_path, checksum_type)
    # Build new URLs for internal repo
    url64_script = f"https://chocoinstall.ldc.com/Packages/googlechrome/{new_version}/googlechromestandaloneenterprise64.msi"
    url_script = f"https://chocoinstall.ldc.com/Packages/googlechrome/{new_version}/googlechromestandaloneenterprise.msi"
    # Update content
    content = re.sub(r"\$version\s*=\s*'[^']+'", f"$version = '{new_version}'", content)
    content = re.sub(r"\$url64\s*=\s*'[^']+'", f"$url64 = '{url64_script}'", content)
    content = re.sub(r"\$url\s*=\s*'[^']+'", f"$url = '{url_script}'", content)
    content = re.sub(r"\$checksum\s*=\s*'[^']+'", f"$checksum = '{checksum}'", content)
    content = re.sub(r"\$checksum64\s*=\s*'[^']+'", f"$checksum64 = '{checksum64}'", content)
    # Write back
    with open(ps1_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_googlechrome_package(pkg, ado_token, username, share_base=None):
    repo_url = pkg['repo_url']
    repo_name = repo_url.split('/')[-1]
    branch_name = f"update-to-{pkg['latest_version']}"
    # Clone repo if not present
    if not os.path.exists(repo_name):
        clone_url = f"https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/{repo_name}"
        subprocess.run([
            "git", "clone", clone_url, repo_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Download and save installers to share
    installer_path, installer64_path = download_and_save_chrome_installers(pkg['latest_version'], share_base, "googlechrome")
    # Update nuspec file programmatically
    nuspec_path = os.path.join(repo_name, "googlechrome.nuspec")
    update_googlechrome_nuspec(nuspec_path, pkg['latest_version'])
    # Update chocolateyinstall.ps1 programmatically
    ps1_path = os.path.join(repo_name, "tools", "chocolateyinstall.ps1")
    update_googlechrome_install_ps1(ps1_path, pkg['latest_version'], installer_path, installer64_path)
    # Create branch, commit, push
    create_and_push_branch(repo_name, branch_name, username, ado_token)
    # Create PR
    create_pull_request(repo_name, branch_name, pkg, ado_token)
    # Clean up repo
    if os.path.exists(repo_name):
        try:
            if os.name == 'nt':
                subprocess.run(["rmdir", "/S", "/Q", repo_name], shell=True)
            else:
                subprocess.run(["rm", "-rf", repo_name])
        except Exception as e:
            print(f"Failed to remove {repo_name}: {e}")

def calculate_checksum(file_path, checksum_type):
    """
    Calculate the checksum of a file using the specified type (e.g., 'sha256', 'sha1', 'md5').
    Returns the hex digest string.
    """
    hash_func = getattr(hashlib, checksum_type, None)
    if hash_func is None:
        raise ValueError(f"Unsupported checksum type: {checksum_type}")
    h = hash_func()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    outdated = []
    for repo_url in AZURE_REPOS:
        repo_name = repo_url.split('/')[-1]
        if not os.path.exists(repo_name):
            clone_url = f"https://dev.azure.com/LDC-Technology-and-Operations/WPM-Chocolatey/_git/{repo_name}"
            subprocess.run(
                ["git", "clone", clone_url, repo_name],
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
                        outdated.append({
                            "package_id": package_id,
                            "local_version": local_version,
                            "latest_version": latest_version,
                            "repo_url": repo_url,
                        })
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
    # Call update function with ADO token and username
    ado_token = config('ADO_TOKEN')
    username = "maslat-ext"
    update_outdated_packages(outdated, ado_token, username)

if __name__ == "__main__":
    main()
