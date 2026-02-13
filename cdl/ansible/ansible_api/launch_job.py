import requests
import json
import urllib3
urllib3.disable_warnings()
from decouple import config

tower_name = 'atwctl.d1.ad.local'
power_control_template_id = '403/launch/'
launch_job_url = f'https://{tower_name}/api/v2/job_templates/'
headers = {"Content-Type": "application/json; charset=utf-8"}
job_url = f"{launch_job_url}{power_control_template_id}"
job_running_statuses = ['pending', 'waiting', 'running']

data = {
    'extra_vars': {
        'target_vm': 'csm1natwvmw001',
        'action': 'deallocate'
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
        completed = True

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
