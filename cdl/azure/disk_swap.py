import re
import logging
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from decouple import config

# user-provided values
vm_name = "csm1natwvmw001"
resource_group = "CSM1NATWRSG001"
subscription_id = "93646852-84e4-4024-8598-7bee49d485c7"
snapshot_name = "csm1natwvmw001-MDK001_01.snap.20251110100207"


TENANT_ID = config('AZURE_TENANT_ID')
CLIENT_ID = config('AZURE_CLIENT_ID')
CLIENT_SECRET = config('AZURE_CLIENT_SECRET')

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
compute_client = ComputeManagementClient(credential, subscription_id)

# 1. get VM info and current disk name
vm = compute_client.virtual_machines.get(resource_group, vm_name)
os_disk = vm.storage_profile.os_disk
current_disk_name = os_disk.name

# Get VM zone (if any)
vm_zones = getattr(vm, 'zones', None)
if vm_zones and len(vm_zones) > 0:
    disk_zones = vm_zones
else:
    disk_zones = None

# 2. parse and increment disk number
match = re.search(r"_(\d{2})$", current_disk_name)
if not match:
    raise ValueError(f"Current disk name '{current_disk_name}' does not match expected pattern.")
current_num = int(match.group(1))
new_num = current_num + 1 if current_num < 99 else 1
new_num_str = f"{new_num:02d}"
new_disk_name = re.sub(r"_(\d{2})$", f"_{new_num_str}", current_disk_name)

# 3. create new disk from snapshot (with zone)
snapshot = compute_client.snapshots.get(resource_group, snapshot_name)
new_disk_params = {
    'location': snapshot.location,
    'creation_data': {
        'create_option': 'Copy',
        'source_resource_id': snapshot.id
    }
}
if disk_zones:
    new_disk_params['zones'] = disk_zones
async_disk_creation = compute_client.disks.begin_create_or_update(resource_group, new_disk_name, new_disk_params)
new_disk = async_disk_creation.result()

# 4. swap the VM's OS disk to the new disk
vm.storage_profile.os_disk.name = new_disk_name
vm.storage_profile.os_disk.managed_disk.id = new_disk.id
async_vm_update = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm)
async_vm_update.result()

# 5. delete the old disk
old_disk_id = os_disk.managed_disk.id
old_disk_name = current_disk_name
compute_client.disks.begin_delete(resource_group, old_disk_name)

logging.info(f"Swapped disk for VM {vm_name}: old disk '{old_disk_name}' deleted, new disk '{new_disk_name}' attached.")
