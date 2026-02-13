#!/usr/bin/env python3
"""
Script to post work notes to ServiceNow change tasks
"""
import ast
import json
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from decouple import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ENVIRONMENT VARIABLES
SNOW_URI = config('SNOW_URI')
SNOW_USERNAME = config('SNOW_USERNAME')
SNOW_PASSWORD = config('SNOW_PASSWORD')
TASK_NUMBER = config('TASK_NUMBER')
WORK_NOTE_MESSAGE = config('WORK_NOTE_MESSAGE')


def post_message_to_task(snow_uri, snow_user, snow_password, task_number, message):
    """
    Posts a message to the 'work_notes' field of the specified change task.

    Args:
        snow_uri: ServiceNow instance URI
        snow_user: ServiceNow username
        snow_password: ServiceNow password
        task_number: The task number (e.g., CTASK0092086)
        message: The message to post in work_notes

    Returns:
        dict: Response containing status and message
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Get the sys_id for the task
    url = f"{snow_uri}/api/now/table/change_task?sysparm_query=number={task_number}"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(snow_user, snow_password),
        headers=headers,
        verify=False
    )

    try:
        sys_id = ast.literal_eval(response._content.decode('utf-8'))["result"][0]["sys_id"]
    except (IndexError, KeyError, TypeError):
        return {
            "failed": True,
            "msg": f"Task {task_number} not found in ServiceNow"
        }

    # Update the task with work_notes
    patch_url = f"{snow_uri}/api/now/table/change_task/{sys_id}"
    payload = {"work_notes": message}

    patch_response = requests.patch(
        patch_url,
        auth=HTTPBasicAuth(snow_user, snow_password),
        headers=headers,
        verify=False,
        data=json.dumps(payload)
    )

    if patch_response.status_code == 200:
        return {
            "failed": False,
            "msg": f"Work note posted successfully to task {task_number}",
            "status_code": patch_response.status_code
        }
    else:
        return {
            "failed": True,
            "msg": f"Failed to post work note to task {task_number}",
            "status_code": patch_response.status_code,
            "response": patch_response.text
        }


def main():
    """Main function to handle execution using environment variables"""
    # Validate environment variables
    if not all([SNOW_URI, SNOW_USERNAME, SNOW_PASSWORD, TASK_NUMBER, WORK_NOTE_MESSAGE]):
        missing = []
        if not SNOW_URI:
            missing.append("SNOW_URI")
        if not SNOW_USERNAME:
            missing.append("SNOW_USERNAME")
        if not SNOW_PASSWORD:
            missing.append("SNOW_PASSWORD")
        if not TASK_NUMBER:
            missing.append("TASK_NUMBER")
        if not WORK_NOTE_MESSAGE:
            missing.append("WORK_NOTE_MESSAGE")

        print(json.dumps({
            "failed": True,
            "msg": f"Missing required environment variables: {', '.join(missing)}"
        }))
        sys.exit(1)

    result = post_message_to_task(SNOW_URI, SNOW_USERNAME, SNOW_PASSWORD, TASK_NUMBER, WORK_NOTE_MESSAGE)
    print(json.dumps(result))

    if result.get("failed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
