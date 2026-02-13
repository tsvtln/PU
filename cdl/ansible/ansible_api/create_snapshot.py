import requests
import json
import urllib3
import time
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
job_id = response.json().get('id')
#print(f"Launched job with ID: {job_id}")

url_monitor = f'https://{tower_name}/api/v2/jobs/{job_id}'
completed = False

while not completed:
    response_mon = requests.get(url_monitor, headers=headers,  auth=(config('USR'), config('PASS')), verify=False)
    response_dict = response_mon.json()
    job_status = response_dict.get("status")
    print(f"Current job status: {job_status}")
    if job_status not in job_running_statuses:
        #print(f"Final job status: {job_status}")
        #print(f'FULL RESPONSE: {response_dict}')
        completed = True
    else:
        time.sleep(2)

# Fetch and print job stdout after completion
if completed and job_status == "successful":
    stdout_url = response_dict.get('related', {}).get('stdout')
    if stdout_url:
        full_stdout_url = f'https://{tower_name}{stdout_url}?format=txt'
        stdout_response = requests.get(full_stdout_url, headers=headers, auth=(config('USR'), config('PASS')), verify=False)
        snapshot_name = stdout_response.text.split('TASK')[24].split(' ')[18].replace("'", '')
        print(f'Snapshot created: {snapshot_name}')
    else:
        print("No stdout URL found in job response.")
else:
    print("Job did not complete successfully or no stdout available.")
