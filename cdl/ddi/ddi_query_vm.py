#!/usr/bin/env python3
"""
Simple standalone script to query DDI for a VM and output the results.
No delete functions included.

Author: tsvetelin.maslarski-ext@ldc.com
"""
import json
from SOLIDserverRest import SOLIDserverRest
from decouple import config

DDI_USER = config('SDS_USER')
DDI_PASS = config('SDS_PASSWORD')
DDI_URL = config('DDI_URL')
VM_NAME = 'csm1kpocvmw926'
VM_IP = '10.242.34.135'

# Connect to DDI
sds_con = SOLIDserverRest(DDI_URL)
sds_con.set_ssl_verify(False)
sds_con.use_basicauth_sds(user=DDI_USER, password=DDI_PASS)

# Query IPAM (ip_address_list) for the VM (case-insensitive, by name or IP)
parameters_ipam_name = {"WHERE": f"LOWER(name) LIKE '%{VM_NAME.lower()}%'"}
parameters_ipam_ip = {"WHERE": f"ip_addr = '{VM_IP}'"}
ipam_result_name = sds_con.query("ip_address_list", parameters_ipam_name)
ipam_result_ip = sds_con.query("ip_address_list", parameters_ipam_ip)

# Query DNS RR (dns_rr_list) for the VM (case-insensitive, by name or IP)
parameters_dns_name = {"WHERE": f"LOWER(rr_name) LIKE '%{VM_NAME.lower()}%'"}
parameters_dns_ip = {"WHERE": f"rr_value = '{VM_IP}'"}
dns_result_name = sds_con.query("dns_rr_list", parameters_dns_name)
dns_result_ip = sds_con.query("dns_rr_list", parameters_dns_ip)

# Query all DNS RR records (no WHERE clause) with increased timeout
try:
    dns_all_result = sds_con.query("dns_rr_list", {}, timeout=15)
except TypeError:
    # fallback if query() does not accept timeout param
    import requests
    orig_request = sds_con._request
    def patched_request(*args, **kwargs):
        kwargs['timeout'] = 60
        return orig_request(*args, **kwargs)
    sds_con._request = patched_request
    dns_all_result = sds_con.query("dns_rr_list", {})

def record_matches(record):
    # Check if the VM name or IP is in any relevant field (case-insensitive)
    rr_name = str(record.get('rr_name', '')).lower()
    rr_value = str(record.get('rr_value', ''))
    # Direct match, substring, or FQDN match
    name_match = (
        VM_NAME.lower() in rr_name or
        rr_name.startswith(VM_NAME.lower()) or
        rr_name == VM_NAME.lower() or
        rr_name.startswith(f"{VM_NAME.lower()}.")
    )
    ip_match = VM_IP in rr_value
    return name_match or ip_match

# Parse all DNS RR records and filter for matches
matching_dns_records = []
if dns_all_result.status_code == 200:
    try:
        all_rrs = json.loads(dns_all_result.content)
        for rr in all_rrs:
            if record_matches(rr):
                matching_dns_records.append(rr)
    except Exception as e:
        matching_dns_records = [f"Error parsing all DNS RR records: {e}"]

# List of endpoints to check for VM name or IP matches
ENDPOINTS_TO_CHECK = [
    ('dns_rr_list', 'rr_name', 'rr_value'),
    ('dns_server_list', 'name', 'ip_addr'),
    ('ip_site_list', 'site_name', 'site_ip_addr'),
    ('ip_block_subnet_list', 'subnet_name', 'subnet_ip_addr'),
    ('ip_pool_list', 'pool_name', 'pool_ip_addr'),
    ('ip_address_list', 'name', 'ip_addr'),
    ('ip_alias_list', 'alias_name', 'alias_ip_addr'),
    ('app_application_list', 'application_name', 'application_ip_addr'),
    ('app_pool_list', 'pool_name', 'pool_ip_addr'),
    ('app_node_list', 'node_name', 'node_ip_addr'),
    ('dhcp_server_list', 'server_name', 'server_ip_addr'),
    ('dhcp_scope_list', 'scope_name', 'scope_ip_addr'),
    ('dhcp_shared_network_list', 'shared_network_name', 'shared_network_ip_addr'),
    ('dhcp_range_list', 'range_name', 'range_ip_addr'),
    ('hostdev_list', 'hostdev_name', 'hostdev_ip_addr'),
    ('hostiface_list', 'hostiface_name', 'hostiface_ip_addr'),
    ('link_hostiface_list', 'link_name', 'link_ip_addr'),
]

def find_matches_in_endpoint(endpoint, name_field, ip_field):
    try:
        result = sds_con.query(endpoint, {}, timeout=60)
        if result.status_code != 200:
            return []
        records = json.loads(result.content)
        matches = []
        for rec in records:
            name_val = str(rec.get(name_field, '')).lower()
            ip_val = str(rec.get(ip_field, ''))
            if VM_NAME.lower() in name_val or VM_NAME.lower() in ip_val or VM_IP in name_val or VM_IP in ip_val:
                matches.append(rec)
        return matches
    except Exception as e:
        return [f"Error querying {endpoint}: {e}"]

endpoint_matches = {}
for endpoint, name_field, ip_field in ENDPOINTS_TO_CHECK:
    matches = find_matches_in_endpoint(endpoint, name_field, ip_field)
    if matches:
        endpoint_matches[endpoint] = matches

output = {
    'ipam_status_code_name': ipam_result_name.status_code,
    'ipam_content_name': ipam_result_name.content.decode() if hasattr(ipam_result_name.content, 'decode') else str(ipam_result_name.content),
    'ipam_status_code_ip': ipam_result_ip.status_code,
    'ipam_content_ip': ipam_result_ip.content.decode() if hasattr(ipam_result_ip.content, 'decode') else str(ipam_result_ip.content),
    'dns_status_code_name': dns_result_name.status_code,
    'dns_content_name': dns_result_name.content.decode() if hasattr(dns_result_name.content, 'decode') else str(dns_result_name.content),
    'dns_status_code_ip': dns_result_ip.status_code,
    'dns_content_ip': dns_result_ip.content.decode() if hasattr(dns_result_ip.content, 'decode') else str(dns_result_ip.content),
    'all_dns_rr_matches': matching_dns_records,
    'endpoint_matches': endpoint_matches
}

print(json.dumps(output, indent=2))
