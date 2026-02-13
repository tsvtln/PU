#!/usr/bin/env python3
"""
Direct test to see if we can get the VM using Azure SDK
"""
import sys
from decouple import config
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

# Credentials
TENANT_ID = config('tenant_id')
CLIENT_ID = config('client_id')
CLIENT_SECRET = config('client_secret')

# Target
SUBSCRIPTION_ID = "fb25bdfb-9077-4e51-a21e-f6a29340caf8"
RESOURCE_GROUP = "CDM1GREPRSG100"
VM_NAME = "CDM1DREPVMR365"

print("="*80)
print("Direct Azure SDK Test")
print("="*80)
print(f"Subscription: {SUBSCRIPTION_ID}")
print(f"Resource Group: {RESOURCE_GROUP}")
print(f"VM Name: {VM_NAME}")
print()

print("Step 1: Creating credentials...")
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    print("✓ Credentials created")
except Exception as e:
    print(f"✗ Failed to create credentials: {e}")
    sys.exit(1)

print("\nStep 2: Creating ComputeManagementClient...")
try:
    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    print("✓ ComputeManagementClient created")
except Exception as e:
    print(f"✗ Failed to create compute client: {e}")
    sys.exit(1)

print(f"\nStep 3: Getting VM '{VM_NAME}' from resource group '{RESOURCE_GROUP}'...")
try:
    vm = compute_client.virtual_machines.get(RESOURCE_GROUP, VM_NAME)
    print("✓ VM retrieved successfully!")
    print(f"  VM Name: {vm.name}")
    print(f"  VM ID: {vm.id}")
    print(f"  Location: {vm.location}")
    print(f"  VM Size: {vm.hardware_profile.vm_size}")

    # Extract resource group from VM ID
    vm_id_parts = vm.id.split('/')
    actual_rg = vm_id_parts[4] if len(vm_id_parts) > 4 else "unknown"
    print(f"  Actual RG from VM ID: {actual_rg}")

except ResourceNotFoundError as e:
    print(f"✗ ResourceNotFoundError: VM not found")
    print(f"  Error message: {e.message if hasattr(e, 'message') else str(e)}")
    print(f"  Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
except HttpResponseError as e:
    print(f"✗ HttpResponseError")
    print(f"  Status code: {e.status_code}")
    print(f"  Error message: {e.message}")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 4: Testing with different case variations...")
for rg_variant in [RESOURCE_GROUP, RESOURCE_GROUP.lower(), RESOURCE_GROUP.title()]:
    print(f"\nTrying resource group: '{rg_variant}'")
    try:
        vm = compute_client.virtual_machines.get(rg_variant, VM_NAME)
        print(f"  ✓ SUCCESS")
    except ResourceNotFoundError:
        print(f"  ✗ NOT FOUND (404)")
    except HttpResponseError as e:
        print(f"  ✗ HTTP ERROR: {e.status_code}")
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}")

print("\n" + "="*80)

