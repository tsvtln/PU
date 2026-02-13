import json
import logging

from SOLIDserverRest import SOLIDserverRest
import mapper
import ddi_exeptions
from decouple import config

def connector():
    SDS_CON = SOLIDserverRest('10.120.5.30')
    SDS_CON.set_ssl_verify(False)
    SDS_CON.use_basicauth_sds(user=config('SDS_USER'), password=config('SDS_PASSWORD'))
    return SDS_CON

# del(SDS_CON)
# ddi_uri: "{{ ddi_url }}/rest/ip_address_list?WHERE={{ encoded_query }}"
# name LIKE'{{ vm_name }}%'

def get_space(name, SDS_CON):
    """get a space by its name from the SDS"""
    parameters = {
        # "WHERE": "site_name='{}'".format(name),
        "WHERE": "name LIKE '%csm1kpocvmw914%'",
        "limit": "1"
    }

    rest_answer = SDS_CON.query("ip_address_list", parameters)

    print(type(rest_answer))

    if rest_answer.status_code != 200:
        logging.error("cannot find space %s", name)
        return ''

    rjson = json.loads(rest_answer.content)

    return {
        'type': 'space',
        'name': name,
        # 'is_default': rjson[0]['site_is_default'],
        'id': rjson[0]['site_id'],
        #'full': rjson
    }

    # 'ip_address_delete': 'ip_delete',

def delete_ipam(SDS_CON, name):
    """delete ip address from SDS"""
    parameters = {
        # "WHERE": "ip_address='{}'".format(ip_address),
        "WHERE": f"name LIKE '%{name}%'",
        # "WHERE": f"ip_address={name}",
        "limit": "1"
    }

    rest_answer = SDS_CON.query("ip_address_list", parameters)

    print(rest_answer)

    if rest_answer.status_code != 200:
        logging.error("cannot find ip address %s", name)
        return False

    rjson = json.loads(rest_answer.content)

    # print(f"RJSON RESPONSE: {rjson}")

    if not rjson:
        logging.error("ip address %s not found", name)
        return False

    ip_id = rjson[0]['ip_id']

    print(ip_id)

    delete_parameters = {
        "ip_id": ip_id
    }

    # delete_answer = SDS_CON.query("ip_delete", delete_parameters)

    delete_answer = SDS_CON.query("ip_address_delete", params=delete_parameters)

    if delete_answer.status_code != 200:
        logging.error("failed to delete ip address %s", name)
        return f'Failed to delete ip address for {name} with IP {ip_id}'

    return f'Successfully deleted ip address for {name} with IP {ip_id}'

def get_space_t(con, name):
    """get a space by its name from the SDS"""
    parameters = {
        "WHERE": "site_name='{}'".format(name),
        "limit": "1"
    }

    rest_answer = con.query("ip_site_list", parameters)

    if rest_answer.status_code != 200:
        logging.error("cannot find space %s", name)
        return None

    rjson = json.loads(rest_answer.content)

    return {
        'type': 'space',
        'name': name,
        # 'is_default': rjson[0]['site_is_default'],
        'id': rjson[0]['site_id']
    }





connector = connector()
# space = get_space("Datacenter", connector)
# print(space)
# space = get_space("CLOUD", connector)
# print(space)
#

# delete = delete_ipam(connector, 'csm1kpocvmw907')
# print(delete)

# space = get_space_t(connector, "CLOUD")
space = get_space('kur', connector)
print(space)
