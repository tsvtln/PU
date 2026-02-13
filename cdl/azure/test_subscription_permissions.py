#!/usr/bin/env python3
"""
Test both working and failing subscriptions to identify permission issue
"""
import sys
from decouple import config
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

# Get credentials from .env
TENANT_ID = config('tenant_id')
CLIENT_ID = config('client_id')
CLIENT_SECRET = config('client_secret')

# Working VM
WORKING_SUBSCRIPTION_ID = "9bcb2324-59e5-4285-a4e5-50725b77107d"
WORKING_RESOURCE_GROUP = "CDM1KIMGRSG901"
WORKING_VM_NAME = "CSM1KPOCVMW916"

# Non-working VM
FAILING_SUBSCRIPTION_ID = "fb25bdfb-9077-4e51-a21e-f6a29340caf8"
FAILING_RESOURCE_GROUP = "CDM1GREPRSG100"
FAILING_VM_NAME = "CDM1DREPVMR365"

print("="*80)
print("Comparing Working vs Failing Subscriptions")
print("="*80)

# Test 1: Working VM (CSM1KPOCVMW916 in subscription 9bcb2324...)
print("\nTest 1: WORKING VM - CSM1KPOCVMW916")
print("-"*80)
print(f"Subscription: {WORKING_SUBSCRIPTION_ID}")
print(f"Resource Group: {WORKING_RESOURCE_GROUP}")
print(f"VM Name: {WORKING_VM_NAME}")
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    print(f"✓ Credential created")

    compute_client = ComputeManagementClient(credential, WORKING_SUBSCRIPTION_ID)
    print(f"✓ ComputeManagementClient created")

    vm = compute_client.virtual_machines.get(WORKING_RESOURCE_GROUP, WORKING_VM_NAME)
    print(f"✓ VM retrieved: {vm.name}")
    print(f"  VM ID: {vm.id}")
    print(f"  Location: {vm.location}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

# Test 2: Failing VM (CDM1DREPVMR365 in subscription fb25bdfb...)
print("\n\nTest 2: FAILING VM - CDM1DREPVMR365")
print("-"*80)
print(f"Subscription: {FAILING_SUBSCRIPTION_ID}")
print(f"Resource Group: {FAILING_RESOURCE_GROUP}")
print(f"VM Name: {FAILING_VM_NAME}")
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    print(f"✓ Credential created")

    compute_client = ComputeManagementClient(credential, FAILING_SUBSCRIPTION_ID)
    print(f"✓ ComputeManagementClient created")

    vm = compute_client.virtual_machines.get(FAILING_RESOURCE_GROUP, FAILING_VM_NAME)
    print(f"✓ VM retrieved: {vm.name}")
    print(f"  VM ID: {vm.id}")
    print(f"  Location: {vm.location}")
except ResourceNotFoundError as e:
    print(f"✗ FAILED - ResourceNotFoundError")
    print(f"  This means the SPN can authenticate but cannot find/access the VM")
    print(f"  Error message: {e.message if hasattr(e, 'message') else str(e)}")
    print(f"  Error details:")
    print(f"    - reason: {e.reason if hasattr(e, 'reason') else 'N/A'}")
    print(f"    - status_code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
    print(f"    - error code: {e.error.code if hasattr(e, 'error') and hasattr(e.error, 'code') else 'N/A'}")
    import traceback
    traceback.print_exc()
except HttpResponseError as e:
    print(f"✗ FAILED - HttpResponseError: {e.status_code}")
    if e.status_code == 403:
        print(f"  This is a PERMISSION DENIED error")
        print(f"  The SPN does not have access to this subscription/resource")
    print(f"  Error message: {e.message}")
    print(f"  Error details:")
    print(f"    - reason: {e.reason if hasattr(e, 'reason') else 'N/A'}")
    print(f"    - error code: {e.error.code if hasattr(e, 'error') and hasattr(e.error, 'code') else 'N/A'}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    print(f"  Exception attributes:")
    for attr in dir(e):
        if not attr.startswith('_'):
            try:
                val = getattr(e, attr)
                if not callable(val):
                    print(f"    - {attr}: {val}")
            except:
                pass
    import traceback
    traceback.print_exc()

# Test 3: List VMs in both resource groups
print("\n\nTest 3: Listing VMs in both resource groups")
print("-"*80)

print(f"\nWorking RG ({WORKING_RESOURCE_GROUP}):")
try:
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    compute_client = ComputeManagementClient(credential, WORKING_SUBSCRIPTION_ID)
    vms = list(compute_client.virtual_machines.list(WORKING_RESOURCE_GROUP))
    print(f"✓ Found {len(vms)} VM(s)")
    for vm in vms[:5]:  # Show first 5
        print(f"  - {vm.name}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print(f"\nFailing RG ({FAILING_RESOURCE_GROUP}):")
try:
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    compute_client = ComputeManagementClient(credential, FAILING_SUBSCRIPTION_ID)
    vms = list(compute_client.virtual_machines.list(FAILING_RESOURCE_GROUP))
    print(f"✓ Found {len(vms)} VM(s)")
    for vm in vms[:5]:  # Show first 5
        print(f"  - {vm.name}")
except HttpResponseError as e:
    if e.status_code == 403:
        print(f"✗ PERMISSION DENIED - SPN cannot list VMs in this resource group")
        print(f"  Status code: {e.status_code}")
        print(f"  Error: {e.message}")
    else:
        print(f"✗ FAILED: HTTP {e.status_code} - {e.message}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check if we can access the resource group itself
print("\n\nTest 4: Checking Resource Group Access")
print("-"*80)
from azure.mgmt.resource import ResourceManagementClient

print(f"\nWorking subscription RG:")
try:
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    resource_client = ResourceManagementClient(credential, WORKING_SUBSCRIPTION_ID)
    rg = resource_client.resource_groups.get(WORKING_RESOURCE_GROUP)
    print(f"✓ Can access RG: {rg.name}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print(f"\nFailing subscription RG:")
try:
    credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    resource_client = ResourceManagementClient(credential, FAILING_SUBSCRIPTION_ID)
    rg = resource_client.resource_groups.get(FAILING_RESOURCE_GROUP)
    print(f"✓ Can access RG: {rg.name}")
except HttpResponseError as e:
    if e.status_code == 403:
        print(f"✗ PERMISSION DENIED - SPN cannot access this resource group")
    print(f"  Status code: {e.status_code}")
    print(f"  Error: {e.message}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n" + "="*80)
print("CONCLUSION:")
print("If Test 2 fails but Test 1 works, the SPN has permissions in")
print("subscription 9bcb2324... but NOT in subscription fb25bdfb...")
print("="*80)

