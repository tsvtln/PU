#!/usr/bin/env python3
"""
Test script to check SPN permissions for accessing VMs in a resource group
"""

import os
import sys
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError, HttpResponseError
from decouple import config

# Configuration
TENANT_ID = config('tenant_id')
CLIENT_ID = config('client_id')
CLIENT_SECRET = config('client_secret')

# Target details - NOT WORKING
RESOURCE_GROUP_NOT_WORKING = "CDM1GREPRSG100"
SUBSCRIPTION_ID_NOT_WORKING = "fb25bdfb-9077-4e51-a21e-f6a29340caf8"
VM_NAME_NOT_WORKING = "CDM1DREPVMR365"

# Target details - WORKING (fill these in)
RESOURCE_GROUP_WORKING = "CDM1KIMGRSG901"
SUBSCRIPTION_ID_WORKING = "9bcb2324-59e5-4285-a4e5-50725b77107d"
VM_NAME_WORKING = "CSM1KPOCVMW916"

# Use the not working one by default
RESOURCE_GROUP = RESOURCE_GROUP_NOT_WORKING
SUBSCRIPTION_ID = SUBSCRIPTION_ID_NOT_WORKING
VM_NAME = VM_NAME_NOT_WORKING

def test_authentication():
    """Test if SPN can authenticate"""
    print("\n" + "="*80)
    print("STEP 1: Testing Authentication")
    print("="*80)

    try:
        credential = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        print(f"✓ Credential object created successfully")
        print(f"  Tenant ID: {TENANT_ID}")
        print(f"  Client ID: {CLIENT_ID}")
        return credential
    except Exception as e:
        print(f"✗ Failed to create credential: {e}")
        sys.exit(1)

def test_subscription_access(credential):
    """Test if SPN can access the subscription"""
    print("\n" + "="*80)
    print("STEP 2: Testing Subscription Access")
    print("="*80)

    try:
        resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
        print(f"✓ Resource client created for subscription: {SUBSCRIPTION_ID}")

        # Try to get subscription details
        try:
            from azure.mgmt.resource import SubscriptionClient
            sub_client = SubscriptionClient(credential)
            sub = sub_client.subscriptions.get(SUBSCRIPTION_ID)
            print(f"✓ Successfully accessed subscription: {sub.display_name}")
            print(f"  State: {sub.state}")
        except Exception as e:
            print(f"⚠ Could not get subscription details: {e}")

        return resource_client
    except Exception as e:
        print(f"✗ Failed to create resource client: {e}")
        sys.exit(1)

def test_resource_group_access(resource_client):
    """Test if SPN can access the resource group"""
    print("\n" + "="*80)
    print("STEP 3: Testing Resource Group Access")
    print("="*80)

    try:
        rg = resource_client.resource_groups.get(RESOURCE_GROUP)
        print(f"✓ Successfully accessed resource group: {RESOURCE_GROUP}")
        print(f"  Location: {rg.location}")
        print(f"  Provisioning State: {rg.properties.provisioning_state}")
        if rg.tags:
            print(f"  Tags: {rg.tags}")
        return True
    except HttpResponseError as e:
        if e.status_code == 404:
            print(f"✗ Resource group '{RESOURCE_GROUP}' not found")
        elif e.status_code == 403:
            print(f"✗ Access denied to resource group '{RESOURCE_GROUP}'")
            print(f"  Error: {e.message}")
        else:
            print(f"✗ HTTP error accessing resource group: {e.status_code} - {e.message}")
        return False
    except Exception as e:
        print(f"✗ Failed to access resource group: {e}")
        return False

def list_all_vms_in_resource_group(credential):
    """List all VMs in the resource group"""
    print("\n" + "="*80)
    print("STEP 4: Listing All VMs in Resource Group")
    print("="*80)

    try:
        compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
        print(f"✓ Compute client created")

        print(f"\nAttempting to list VMs in resource group: {RESOURCE_GROUP}")

        vms = list(compute_client.virtual_machines.list(RESOURCE_GROUP))

        if not vms:
            print(f"⚠ No VMs found in resource group '{RESOURCE_GROUP}'")
            print(f"  This could mean:")
            print(f"    - The resource group is empty")
            print(f"    - The SPN doesn't have permission to list VMs")
            print(f"    - The resource group name is incorrect")
            return []

        print(f"\n✓ Found {len(vms)} VM(s) in resource group '{RESOURCE_GROUP}':")
        print("-" * 80)

        for vm in vms:
            print(f"\nVM Name: {vm.name}")
            print(f"  ID: {vm.id}")
            print(f"  Location: {vm.location}")
            print(f"  VM Size: {vm.hardware_profile.vm_size}")
            print(f"  OS Type: {vm.storage_profile.os_disk.os_type}")
            if vm.zones:
                print(f"  Zones: {vm.zones}")
            if vm.tags:
                print(f"  Tags: {vm.tags}")

        return vms

    except HttpResponseError as e:
        if e.status_code == 403:
            print(f"✗ Access denied when listing VMs")
            print(f"  Error: {e.message}")
            print(f"\n  The SPN likely needs the following permissions:")
            print(f"    - Reader role on the resource group")
            print(f"    - OR Virtual Machine Contributor role")
        else:
            print(f"✗ HTTP error listing VMs: {e.status_code} - {e.message}")
        return []
    except Exception as e:
        print(f"✗ Failed to list VMs: {type(e).__name__}: {e}")
        return []

def test_specific_vm_access(credential, vm_name):
    """Test if SPN can access a specific VM"""
    print("\n" + "="*80)
    print(f"STEP 5: Testing Access to Specific VM: {vm_name}")
    print("="*80)

    try:
        compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

        print(f"\nAttempting to get VM: {vm_name}")
        vm = compute_client.virtual_machines.get(
            RESOURCE_GROUP,
            vm_name,
            expand='instanceView'
        )

        print(f"✓ Successfully accessed VM: {vm.name}")
        print(f"  ID: {vm.id}")
        print(f"  Location: {vm.location}")
        print(f"  VM Size: {vm.hardware_profile.vm_size}")
        print(f"  OS Type: {vm.storage_profile.os_disk.os_type}")

        if vm.zones:
            print(f"  Zones: {vm.zones}")

        # Get power state
        if vm.instance_view and vm.instance_view.statuses:
            for status in vm.instance_view.statuses:
                if status.code.startswith('PowerState/'):
                    power_state = status.code.split('/')[-1]
                    print(f"  Power State: {power_state}")
                    break

        # Get disks
        if vm.storage_profile.data_disks:
            print(f"  Data Disks: {len(vm.storage_profile.data_disks)}")
            for disk in vm.storage_profile.data_disks:
                print(f"    - {disk.name} (LUN {disk.lun})")

        if vm.tags:
            print(f"  Tags:")
            for key, value in vm.tags.items():
                print(f"    {key}: {value}")

        return vm

    except HttpResponseError as e:
        if e.status_code == 404:
            print(f"✗ VM '{vm_name}' not found in resource group '{RESOURCE_GROUP}'")
            print(f"  Error: {e.message}")
        elif e.status_code == 403:
            print(f"✗ Access denied to VM '{vm_name}'")
            print(f"  Error: {e.message}")
        else:
            print(f"✗ HTTP error accessing VM: {e.status_code} - {e.message}")
        return None
    except Exception as e:
        print(f"✗ Failed to access VM: {type(e).__name__}: {e}")
        return None

def test_permissions_details(credential):
    """Test detailed permissions"""
    print("\n" + "="*80)
    print("STEP 6: Testing Detailed Permissions")
    print("="*80)

    try:
        from azure.mgmt.authorization import AuthorizationManagementClient

        auth_client = AuthorizationManagementClient(credential, SUBSCRIPTION_ID)

        # Get role assignments for the resource group
        scope = f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}"

        print(f"\nAttempting to list role assignments for resource group...")
        assignments = list(auth_client.role_assignments.list_for_scope(scope))

        print(f"✓ Found {len(assignments)} role assignment(s) in resource group")

        # Try to find assignments for our SPN
        our_assignments = [a for a in assignments if CLIENT_ID in str(a.principal_id)]

        if our_assignments:
            print(f"\n✓ Found {len(our_assignments)} role assignment(s) for this SPN:")
            for assignment in our_assignments:
                print(f"  - Role: {assignment.role_definition_id.split('/')[-1]}")
                print(f"    Scope: {assignment.scope}")
        else:
            print(f"\n⚠ No direct role assignments found for this SPN")
            print(f"  The SPN may have inherited permissions from subscription or management group")

    except HttpResponseError as e:
        if e.status_code == 403:
            print(f"⚠ No permission to list role assignments")
            print(f"  This is normal - the SPN doesn't need this permission to access VMs")
        else:
            print(f"⚠ Could not check permissions: {e.message}")
    except Exception as e:
        print(f"⚠ Could not check permissions: {type(e).__name__}: {e}")

def test_resource_group_case_sensitivity(credential):
    """Test if resource group name is case sensitive"""
    print("\n" + "="*80)
    print("STEP 7: Testing Resource Group Case Sensitivity")
    print("="*80)

    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

    # Try different case variations
    rg_variations = [
        RESOURCE_GROUP,
        RESOURCE_GROUP.upper(),
        RESOURCE_GROUP.lower(),
        RESOURCE_GROUP.title()
    ]

    print(f"\nTrying to get VM '{VM_NAME}' with different resource group case variations:")
    print("-" * 80)

    for rg_variant in rg_variations:
        try:
            print(f"\nTrying resource group: '{rg_variant}'")
            vm = compute_client.virtual_machines.get(rg_variant, VM_NAME)
            print(f"  ✓ SUCCESS - VM retrieved")
            print(f"    Actual RG from VM object: {vm.id.split('/')[4]}")
        except HttpResponseError as e:
            if e.status_code == 404:
                print(f"  ✗ NOT FOUND - 404 error")
            elif e.status_code == 403:
                print(f"  ✗ FORBIDDEN - 403 error")
            else:
                print(f"  ✗ ERROR - {e.status_code}: {e.message}")
        except Exception as e:
            print(f"  ✗ ERROR - {type(e).__name__}: {e}")

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("Azure SPN Permission Test")
    print("="*80)
    print(f"\nTarget Configuration:")
    print(f"  Subscription ID: {SUBSCRIPTION_ID}")
    print(f"  Resource Group: {RESOURCE_GROUP}")
    print(f"  Target VM: {VM_NAME}")

    # Step 1: Test authentication
    credential = test_authentication()

    # Step 2: Test subscription access
    resource_client = test_subscription_access(credential)

    # Step 3: Test resource group access
    rg_accessible = test_resource_group_access(resource_client)

    if not rg_accessible:
        print("\n" + "="*80)
        print("CONCLUSION: Cannot access resource group - stopping tests")
        print("="*80)
        sys.exit(1)

    # Step 4: List all VMs
    vms = list_all_vms_in_resource_group(credential)

    # Step 5: Test specific VM access
    vm = test_specific_vm_access(credential, VM_NAME)

    # Step 6: Check permissions (optional)
    test_permissions_details(credential)

    # Step 7: Test case sensitivity
    test_resource_group_case_sensitivity(credential)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Authentication: SUCCESS")
    print(f"✓ Subscription Access: SUCCESS")
    print(f"{'✓' if rg_accessible else '✗'} Resource Group Access: {'SUCCESS' if rg_accessible else 'FAILED'}")
    print(f"{'✓' if vms else '✗'} List VMs: {'SUCCESS' if vms else 'FAILED'} ({len(vms)} VM(s) found)")
    print(f"{'✓' if vm else '✗'} Access Specific VM: {'SUCCESS' if vm else 'FAILED'}")

    if not vms and rg_accessible:
        print("\n⚠ WARNING: Resource group is accessible but no VMs found!")
        print("  Possible reasons:")
        print("    1. The SPN doesn't have 'Reader' or 'Virtual Machine Contributor' role")
        print("    2. The resource group name has wrong casing (should be case-insensitive but check anyway)")
        print("    3. The VMs are in a different resource group")
        print("    4. There's a resource policy blocking access")

    if not vm and vms:
        print(f"\n⚠ WARNING: Other VMs found but '{VM_NAME}' is not accessible!")
        print("  Possible reasons:")
        print("    1. VM name is incorrect or has wrong casing")
        print("    2. VM was recently deleted or moved")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()

