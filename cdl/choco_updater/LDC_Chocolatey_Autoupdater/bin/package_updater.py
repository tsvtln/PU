import logging

from vars.global_vars import GlobalVars


class PackageUpdater(GlobalVars):
    def __init__(self):
        super().__init__()
        self.updaters = self.get_updaters()

    def update_outdated_packages(self):
        for pkg in self.outdated_packages:
            package_id = pkg["package_id"]
            if package_id not in self.updaters.keys():
                logging.error(f"Package {package_id} is not configured for update.")
                continue
            elif package_id.lower() == 'googlechrome':
                logging.info(f"Updating Google Chrome package {package_id}.")
                self.updaters['googlechrome'].update_package(pkg, self.share_base)
            elif package_id.lower() == 'package':
                ...  # Placeholder for future package updaters
