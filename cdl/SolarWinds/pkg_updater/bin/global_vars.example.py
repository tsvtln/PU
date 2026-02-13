import os

class GlobalVars:
    # DO NOT MODIFY the variables below
    solarwinds_version = ''
    solarwinds_fileshare_path = '\\\\csm1pdmlsto002.file.core.windows.net\\chocolatey\\solarwinds-agent'
    swawaone_checksum = ''  # SolarWinds-Agent-Windows-Active-001.7z
    swawatwo_checksum = ''  # SolarWinds-Agent-Windows-Active-002.7z
    swawp_checksum = ''  # Solarwinds-Agent-Windows-Passive.zip
    srone_checksum = ''  # swagent-rhel-001.tar.gz
    srtwo_checksum = '' # swagent-rhel-002.tar.gz
    srp_checksum = '' # swiagent-rhel-passive.tar.gz
    cache_dir = os.path.join('C:\\', 'Temp', 'sw_pkg_updater_cache')
    branch_name = ''
    pull_request_url = ''

    # Modify bellow accordingly
    ado_token = ''  # ADO personal access token (PAT) here.
    ado_username = ''  # ADO username. Example: maslat-ext
    git_user_name = '' # ADO for git push associated username here. Example: Tsvetelin.Maslarski
    git_user_email = ''  # ADO for git push associated email here. Example: tsvetelin.maslarski-ext@ldc.com
    fileshare_username = ''  # Add username for fileshare access here. Example: GLOBAL\\MASLAT-ADM
    fileshare_password = ''  # Add password for fileshare access here