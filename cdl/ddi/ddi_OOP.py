import json
import logging

from SOLIDserverRest import SOLIDserverRest
import mapper
import ddi_exeptions


class DDIRunner(mapper, ddi_exeptions):
    def __init__(self, message=""):
        self.connector = self.connector()

    @staticmethod
    def connector():
        SDS_CON = SOLIDserverRest('10.120.5.30/rest')
        SDS_CON.set_ssl_verify(False)
        SDS_CON.use_basicauth_sds(user='', password='')
        return SDS_CON

    # del(SDS_CON)
    # ddi_uri: "{{ ddi_url }}/rest/ip_address_list?WHERE={{ encoded_query }}"

    def get_space(self, name, SDS_CON):
        """get a space by its name from the SDS"""
        parameters = {
            "WHERE": "site_name='{}'".format(name),
            "limit": "1"
        }

        rest_answer = SDS_CON.query("ip_site_list", parameters)

        if rest_answer.status_code != 200:
            logging.error("cannot find space %s", name)
            return None

        rjson = json.loads(rest_answer.content)

        return {
            'type': 'space',
            'name': name,
            # 'is_default': rjson[0]['site_is_default'],
            'id': rjson[0]['site_id'],
            'full': rjson
        }


# connector = connector()
space = get_space("CLOUD", connector)
print(space)



