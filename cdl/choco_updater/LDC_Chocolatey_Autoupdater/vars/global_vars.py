from decouple import config
import os


class GlobalVars:
    cache_dir = None

    ado_token = config('ADO_TOKEN')
    ado_username = 'maslat-ext'
    log_name = os.path.join('logs')


    # URLs and namespaces
    nuspec_schema = 'http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd'
    choco_api = 'https://community.chocolatey.org/api/v2/'
    d_version = './/{http://schemas.microsoft.com/ado/2007/08/dataservices}Version'
    azure_url = 'dev.azure.com'
    ldc_choco_url = "https://chocoinstall.ldc.com/Packages/"
    organization = 'LDC-Technology-and-Operations'
    project = 'WPM-Chocolatey'
    outdated_packages = []
    cwd: str = os.getcwd()
    share_base = r"\\csm1pdmlsto002.file.core.windows.net\chocolatey"

    # Updaters
    @staticmethod
    def get_updaters():
        from libs.package_modules.google_chrome import GoogleChrome
        return {
            'googlechrome': GoogleChrome(
                GlobalVars.ldc_choco_url,
                GlobalVars.azure_url,
                GlobalVars.organization,
                GlobalVars.project
            ),
        }
