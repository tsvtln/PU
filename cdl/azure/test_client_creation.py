#!/usr/bin/env python3
"""
Reproduce the exact SnapShotManager client creation pattern to debug
"""
import os
import sys
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import ResourceNotFoundError
from decouple import config

# Set credentials
TENANT_ID = config('tenant_id')
CLIENT_ID = config('client_id')
CLIENT_SECRET = config('client_secret')
SUBSCRIPTION_ID = "fb25bdfb-9077-4e51-a21e-f6a29340caf8"
RESOURCE_GROUP = "CDM1GREPRSG100"
VM_NAME = "CDM1DREPVMR365"

print("="*80)
print("Testing SnapShotManager Client Creation Pattern")
print("="*80)

# Test 1: Using positional argument (like test_direct_api.py - WORKS)
print("\nTest 1: ComputeManagementClient(credential, subscription_id) - POSITIONAL")
print("-"*80)
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    print(f"✓ Credential created")

    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    print(f"✓ ComputeManagementClient created (positional arg)")

    vm = compute_client.virtual_machines.get(RESOURCE_GROUP, VM_NAME)
    print(f"✓ VM retrieved: {vm.name}")
    print(f"  VM ID: {vm.id}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

# Test 2: Using keyword argument (like original create_snapshot.py - might FAIL)
print("\n\nTest 2: ComputeManagementClient(credential, subscription_id=...) - KEYWORD")
print("-"*80)
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    print(f"✓ Credential created")

    compute_client = ComputeManagementClient(credential, subscription_id=SUBSCRIPTION_ID)
    print(f"✓ ComputeManagementClient created (keyword arg)")

    vm = compute_client.virtual_machines.get(RESOURCE_GROUP, VM_NAME)
    print(f"✓ VM retrieved: {vm.name}")
    print(f"  VM ID: {vm.id}")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

# Test 3: Check the ComputeManagementClient signature
print("\n\nTest 3: Inspecting ComputeManagementClient signature")
print("-"*80)
import inspect
sig = inspect.signature(ComputeManagementClient.__init__)
print(f"ComputeManagementClient.__init__ signature:")
print(f"  {sig}")

# Test 4: Check what subscription_id is set to in the client
print("\n\nTest 4: Checking subscription_id in client objects")
print("-"*80)
try:
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    client1 = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    print(f"Client 1 (positional): subscription_id = '{client1.subscription_id}'")

    client2 = ComputeManagementClient(credential, subscription_id=SUBSCRIPTION_ID)
    print(f"Client 2 (keyword):    subscription_id = '{client2.subscription_id}'")

    if client1.subscription_id == client2.subscription_id:
        print("✓ Both clients have the same subscription_id")
    else:
        print("✗ WARNING: Clients have different subscription_id!")

except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n" + "="*80)

