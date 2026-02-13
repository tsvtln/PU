import requests
import json
import urllib3
urllib3.disable_warnings()
from decouple import config

tower_name = 'atwctl.d1.ad.local'
power_control_template_id = '356/launch/'
launch_job_url = f'https://{tower_name}/api/v2/job_templates/'
headers = {"Content-Type": "application/json; charset=utf-8"}
job_url = f"{launch_job_url}{power_control_template_id}"
job_running_statuses = ['pending', 'waiting', 'running']

data = {
        'extra_vars': {
        "vm_name": "csm1natwvmw001",
        "deletion_days": 3
    }
}


response = requests.post(job_url, headers=headers, json=data, auth=(config('USR'), config('PASS')), verify=False)
#print(response)
#print("Status Code", response.status_code)
#print("JSON Response ", response.json())
job_id = response.json().get('id')

print('\n')
print('\n')
print('\n')
print('\n')
print('\n')

url_monitor = f'https://{tower_name}/api/v2/jobs/{job_id}'
# url_monitor = f'https://{tower_name}/api/v2/jobs/120353'

completed = False

while not completed:
    response_mon = requests.get(url_monitor, headers=headers,  auth=('LDC-P-S-ATW-AUT-001', '0ynXZ0HZmpveLYzrCKpZ'), verify=False)
    response_dict = response_mon.json()
    status = response_dict["summary_fields"]["project"]["status"]
    # print(f'RESPONSE DICT: {response_dict["summary_fields"]["project"]["status"]}')
    if status not in job_running_statuses:
        print(status)
        print(f'FULL RESPONSE: {response_dict}')
        completed = True

# Fetch and print job stdout after completion
if completed:
    # Get the stdout URL from the job details
    stdout_url = response_dict.get('related', {}).get('stdout')
    if stdout_url:
        full_stdout_url = f'https://{tower_name}{stdout_url}?format=txt'
        stdout_response = requests.get(full_stdout_url, headers=headers, auth=('LDC-P-S-ATW-AUT-001', '0ynXZ0HZmpveLYzrCKpZ'), verify=False)
        print("\n--- Job STDOUT ---\n")
        print(stdout_response.text)
    else:
        print("No stdout URL found in job response.")

#
# response = requests.get(job_url, verify=False)
#
# if response.status_code == 200:
#     logging.info(f"Package {package_id} found in ATW.")
#     return True
# elif response.status_code == 404:
#     logging.info(f"Package {package_id} not found in ATW.")
#     return False
# else:
#     logging.error(f"Failed to check package {package_id} in ATW. "
#                   f"Response code: {response.status_code}, Response: {response.text}")
#     return False

