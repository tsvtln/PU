import ast
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from decouple import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

snow_user = "LDC-T-SNOW-ANSB"
snow_password = config('PASS')
headers = {"Content-Type": "application/json", "Accept": "application/json"}


def chqs():
    # url = "https://ldcdev.service-now.com/api/now/table/change_task?sysparm_fields=change_request&sysparm_query=number=CTASK0092086"
    url = "https://ldcdev.service-now.com/api/now/table/change_task?sysparm_fields=change_request&sysparm_query=number=CTASK0168861"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.get(url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)
    response_text = response._content
    response_values = ast.literal_eval(response_text.decode('utf-8'))
    #chr_value = response_values["result"][0]["change_request"]["value"]
    # one_shot_chr = ast.literal_eval(
    #             requests.get(
    #                 url,
    #                 auth=HTTPBasicAuth(snow_user, snow_password),
    #                 headers=headers, verify=False)._content.decode('utf-8'))["result"][0]["change_request"]["value"]

    try:
        return ast.literal_eval(requests.get(url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)._content.decode('utf-8'))["result"][0]["change_request"]["value"]
    except IndexError:
        return None

print(chqs())

################################################
chr_value = "f025fd5dc3d4fe14f67d30ba050131ab"
# chr_value = "6c1c6e7e87c9c5107e0c0d86cebb354d"

#url_tasks = f"https://ldcdev.service-now.com/api/now/table/change_task?sysparm_fields=change_request,number,short_description&sysparm_query=change_requestvalue={chr_value}"
# Get all fields by omitting sysparm_fields
url_tasks = f"https://ldcdev.service-now.com/api/now/table/change_task?sysparm_query=change_requestvalue={chr_value}"
response_tasks = requests.get(url_tasks, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)
tasks_content = response_tasks._content
tasks_values = ast.literal_eval(tasks_content.decode('utf-8'))

one_shot_tasks = ast.literal_eval(
            (requests.get(
                url_tasks,
                headers=headers,
                auth=HTTPBasicAuth(snow_user, snow_password), verify=False))._content.decode('utf-8'))

# print(response)
#print(one_shot_tasks)
# print(one_shot_chr)
#response_dict = dict(response_text)
#print(url_tasks)
#print(json.dumps(response_tasks.text, indent=2))
#print(tasks_values["result"])


def post_message_to_task(task_number, message):
    """
    Posts a message to the 'work_notes' field of the specified change task.
    """
    url = f"https://ldcdev.service-now.com/api/now/table/change_task?sysparm_query=number={task_number}"
    response = requests.get(url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)
    try:
        sys_id = ast.literal_eval(response._content.decode('utf-8'))["result"][0]["sys_id"]
    except (IndexError, KeyError, TypeError):
        print(f"Task {task_number} not found.")
        return
    patch_url = f"https://ldcdev.service-now.com/api/now/table/change_task/{sys_id}"
    payload = {"work_notes": message}
    patch_response = requests.patch(patch_url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False, data=json.dumps(payload))
    if patch_response.status_code == 200:
        print(f"Message posted to {task_number}.")
    else:
        print(f"Failed to post message to {task_number}. Response: {patch_response.text}")


def set_task_status(task_number, state_value):
    """
    Updates the 'state' field (status) of the specified change task.
    state_value should be an integer corresponding to the desired status.
    Also attempts to update the 'description' field for troubleshooting.
    """
    url = f"https://ldcdev.service-now.com/api/now/table/change_task?sysparm_query=number={task_number}"
    response = requests.get(url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)
    try:
        sys_id = ast.literal_eval(response._content.decode('utf-8'))["result"][0]["sys_id"]
    except (IndexError, KeyError, TypeError):
        print(f"Task {task_number} not found.")
        return
    patch_url = f"https://ldcdev.service-now.com/api/now/table/change_task/{sys_id}"
    payload_state = {"state": state_value}
    patch_response_state = requests.patch(patch_url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False, data=json.dumps(payload_state))
    print(f"PATCH state response for {task_number}: {patch_response_state.status_code} {patch_response_state.text}")
    payload_desc = {"description": "API test update"}
    patch_response_desc = requests.patch(patch_url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False, data=json.dumps(payload_desc))
    print(f"PATCH description response for {task_number}: {patch_response_desc.status_code} {patch_response_desc.text}")
    if patch_response_state.status_code == 200:
        print(f"Status of {task_number} updated to {state_value}.")
    else:
        print(f"Failed to update status of {task_number}.")

def close_task(task_number, close_notes="Closed by API", close_code="Closed"):
    """
    Attempts to close the specified change task by setting state=3 and close_notes/close_code if available.
    """
    url = f"https://ldcdev.service-now.com/api/now/table/change_task?sysparm_query=number={task_number}"
    response = requests.get(url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False)
    try:
        sys_id = ast.literal_eval(response._content.decode('utf-8'))["result"][0]["sys_id"]
    except (IndexError, KeyError, TypeError):
        print(f"Task {task_number} not found.")
        return
    patch_url = f"https://ldcdev.service-now.com/api/now/table/change_task/{sys_id}"
    payload = {"state": 3, "close_notes": close_notes, "close_code": close_code}
    patch_response = requests.patch(patch_url, auth=HTTPBasicAuth(snow_user, snow_password), headers=headers, verify=False, data=json.dumps(payload))
    print(f"PATCH close response for {task_number}: {patch_response.status_code} {patch_response.text}")
    if patch_response.status_code == 200:
        print(f"Task {task_number} closed.")
    else:
        print(f"Failed to close task {task_number}.")

for item in tasks_values["result"]:
    try:
        #print(item["change_request"]["link"])
        number = item["number"]
        change_request = item["change_request"]
        change_request_link = change_request["link"]
        change_request_value = change_request["value"]
        short_description = item["short_description"]
        if change_request_value == chr_value:
            #print(f"Task Number: {number}, Change Request Link: {change_request_link}, Change Request Value: {change_request_value}")
            #print(f"Task Number: {number}, CHR: {change_request_value}, Short Description: {short_description}")
            var = 1
            if short_description == '2. Part Two Tasks' or short_description == '1. Part One Tasks':
                print(f"CHR: {change_request_value}, Task Number: {number}, Short Description: {short_description} - KEEP")
                post_message_to_task(number, "Hello world")
                # Attempt to close the task
                close_task(number)
    except TypeError:
        continue