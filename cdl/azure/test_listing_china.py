#!/usr/bin/env python3
import os
import logging
import http.client
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError
from decouple import config

# Enable HTTP and Azure SDK debugging
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("azure").setLevel(logging.DEBUG)


#os.environ['REQUESTS_CA_BUNDLE'] = '/home/maslat-adm/gitworkdir/tsvtln_bin/azure/china_root_ca.pem'
#os.environ['SSL_CERT_FILE'] = '/home/maslat-adm/gitworkdir/tsvtln_bin/azure/china_root_ca.pem'
# os.environ['REQUESTS_CA_BUNDLE'] = "C:\\pjs\\tsvtln_bin\\azure\\china_root_ca.pem"
# os.environ['SSL_CERT_FILE'] = "C:\\pjs\\tsvtln_bin\\azure\\china_root_ca.pem"
# os.environ['REQUESTS_CA_BUNDLE'] = '/etc/pki/ca-trust/source/anchors/Netskope-IntermediatecaCert_2034.crt'
# os.environ['REQUESTS_CA_BUNDLE'] = '/etc/pki/ca-trust/source/anchors/Netskope-RootcaCert_2034.crt'
# os.environ['SSL_CERT_FILE'] = '/etc/pki/ca-trust/source/anchors/Netskope-RootcaCert_2034.crt'


# Azure China environment
credential = ClientSecretCredential(
    tenant_id=config('tenant_id_china'),
    client_id=config('client_id_china'),
    client_secret=config('client_secret_china'),
    authority=AzureAuthorityHosts.AZURE_CHINA
)

subscription_id = "e21766fd-4d1f-49b7-ac3d-a9ed83bfc3b1"
resource_group = "CSM4VDACRSG001"

compute_client = ComputeManagementClient(
    credential,
    subscription_id,
    base_url="https://management.chinacloudapi.cn",
    credential_scopes=["https://management.chinacloudapi.cn/.default"],
    connection_verify=False  # Disable SSL verification
)

try:
    print("Listing all VMs in RG:", resource_group)
    vms = compute_client.virtual_machines.list(resource_group)
    for vm in vms:
        print("Resource VM name:", vm.name)

        details = compute_client.virtual_machines.get(resource_group, vm.name, expand='instanceView')
        if details.os_profile:
            print("Computer name:", details.os_profile.computer_name)
        if details.instance_view and details.instance_view.statuses:
            for status in details.instance_view.statuses:
                if "PowerState" in status.code:
                    print("State:", status.display_status)

except HttpResponseError as e:
    print("Error occurred:", e.message)
    print("Status code:", e.status_code)