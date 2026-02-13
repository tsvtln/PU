#!/bin/bash

# variables
start_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
scope="/providers/Microsoft.Management/managementGroups/LDC-Root/"
principal_id="f77035c6-a019-48d2-922c-a36dfed35a9f"
role_definition_id="/providers/Microsoft.Management/managementGroups/LDC-Root/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"
justification="Ansible Automation"
duration="PT8H"

# get access token for microsoft graph in azure china
access_token=$(az account get-access-token --resource https://microsoftgraph.chinacloudapi.cn --query accessToken -o tsv)

# prepare the request body
read -r -d '' body <<EOF
{
  "action": "selfActivate",
  "justification": "$justification",
  "principalId": "$principal_id",
  "roleDefinitionId": "$role_definition_id",
  "resourceScope": "$scope",
  "scheduleInfo": {
    "startDateTime": "$start_time",
    "expiration": {
      "type": "afterDuration",
      "duration": "$duration"
    }
  }
}
EOF

# make the api call to the china graph endpoint
curl -X POST "https://microsoftgraph.chinacloudapi.cn/beta/roleManagement/entitlementManagement/roleAssignmentScheduleRequests" \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "$body"

echo "PIM role assignment schedule request submitted (Azure China)."
