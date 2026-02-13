#!/usr/bin/env python3
"""
Test script to directly call the snapshot creation logic
This mimics what Ansible does when calling create_snapshot.py
"""

import os
import sys
from decouple import config

# DON'T redirect stderr - we want to see it separately
# sys.stderr = sys.stdout

# Set environment variables exactly as Ansible would
os.environ["VM_NAME"] = "CDM1DREPVMR365"
os.environ["RESOURCE_GROUP"] = "CDM1GREPRSG100"
os.environ["SUBSCRIPTION_ID"] = "fb25bdfb-9077-4e51-a21e-f6a29340caf8"
os.environ["AZURE_CLIENT_ID"] = config('client_id')
os.environ["AZURE_CLIENT_SECRET"] = config('client_secret')
os.environ["AZURE_TENANT_ID"] = config('tenant_id')
os.environ["CHINA_TENANT_ID"] = config('tenant_id_china')
os.environ["CHINA_CLIENT_ID"] = config('client_id_china')
os.environ["CHINA_CLIENT_SECRET"] = config('client_secret_china')
os.environ["DELETION_BASE_DATE"] = "2025-10-28"
os.environ["DELETION_DAYS_CLAMPED"] = "3"

# Add the path to the create_snapshot script
sys.path.insert(0, r'C:\pjs\ATW\LDC_role_Azure_VM_snapshot\files')

# Import and run
from create_snapshot import SnapShotManager

print("\n" + "="*80)
print("Testing Snapshot Creation (mimicking Ansible)")
print("="*80)
print(f"\nEnvironment Variables:")
print(f"  VM_NAME: {os.environ['VM_NAME']}")
print(f"  RESOURCE_GROUP: {os.environ['RESOURCE_GROUP']}")
print(f"  SUBSCRIPTION_ID: {os.environ['SUBSCRIPTION_ID']}")
print(f"  AZURE_TENANT_ID: {os.environ['AZURE_TENANT_ID']}")
print(f"  AZURE_CLIENT_ID: {os.environ['AZURE_CLIENT_ID']}")

print("\n" + "-"*80)
print("Creating snapshot manager...")
print("-"*80)

try:
    snapshot_manager = SnapShotManager()
    result = snapshot_manager.printer()
    print("\nResult:")
    print(result)
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

