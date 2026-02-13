resource='/subscriptions/8d88d37b-e553-4c98-8c41-930abc3412d8/resourceGroups/BSM1KBKPRSGI01/providers/Microsoft.Compute/virtualMachines/veeam-linux-helper-appliance-qbddq'
parts = resource.split("/")
print(parts)
print(f'sub_id = {parts[2]}')
print(f'rg_name = {parts[4]}')