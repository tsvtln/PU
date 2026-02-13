import os

class GlobalVars:
    solarwinds_version = ''
    solarwinds_fileshare_path = '\\\\csm1pdmlsto002.file.core.windows.net\\chocolatey\\solarwinds-agent'
    swawaone_checksum = ''  # SolarWinds-Agent-Windows-Active-001.7z
    swawatwo_checksum = ''  # SolarWinds-Agent-Windows-Active-002.7z
    swawp_checksum = ''  # Solarwinds-Agent-Windows-Passive.zip
    srone_checksum = ''  # swagent-rhel-001.tar.gz
    srtwo_checksum = '' # swagent-rhel-002.tar.gz
    srp_checksum = '' # swiagent-rhel-passive.tar.gz

    # Secrets: provide at runtime via environment variables
    ado_token = os.environ.get('ADO_TOKEN', '')
    ado_username = os.environ.get('ADO_USERNAME', '')
    git_user_name = os.environ.get('GIT_USER_NAME', '')
    git_user_email = os.environ.get('GIT_USER_EMAIL', '')

    cache_dir = os.path.join('C:\\', 'Temp', 'sw_pkg_updater_cache')
    branch_name = ''
    pull_request_url = ''

    # creds for the fileshare mounting
    fileshare_username = os.environ.get('FILESHARE_USERNAME', '')
    fileshare_password = os.environ.get('FILESHARE_PASSWORD', '')
