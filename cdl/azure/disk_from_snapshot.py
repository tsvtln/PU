# storage array for all found disks
disks = []

# Get OS disk
if vm.storage_profile.os_disk:
    os_disk_id = vm.storage_profile.os_disk.managed_disk.id
    # Parse the disk resource group from the disk ID
    # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/disks/{disk_name}
    disk_id_parts = os_disk_id.split('/')
    if len(disk_id_parts) >= 9:
        disk_resource_group = disk_id_parts[4]  # Get the actual RG of the disk
        os_disk_name = disk_id_parts[8]  # Get the disk name
    else:
        # Fallback to old behavior if ID format is unexpected
        disk_resource_group = self.resource_group
        os_disk_name = vm.storage_profile.os_disk.name

    try:
        os_disk = self.compute_client.disks.get(disk_resource_group, os_disk_name)
        disks.append({
            'name': os_disk.name,
            'type': 'OS',
            'size_gb': os_disk.disk_size_gb,
            'sku': os_disk.sku.name if os_disk.sku else None,
            'disk_object': os_disk
        })
    except ResourceNotFoundError:
        self._result['msg'] = f"OS Disk '{os_disk_name}' not found in resource group '{disk_resource_group}'"
        self._result['failed'] = True
        return []

...

# Delete disk
compute_client.disks.begin_delete(
    GROUP_NAME,
    DISK_NAME
).result()
print("Delete disk.\n")