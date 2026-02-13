# /usr/bin/ptyhon
"""
ORION SDK base.
@tsvtln

// V1.03
        Added automation for checkbox/memory poller
        // TODO Configure the credentials handling with OpCon and use it instead of FERNET.
// v1.04
        Added sw_agent_manager.
            SW will connect the agent which is already installed on a machine as
            passive agent on port 17790.

// v1.05
        Added sw_delete_agent
            Gets an agentId based on hostname and deletes the agent.

// v1.06
        Added sw_unmanage_agent
            Gets the NodeID by hostname and unamanages the agent in SW.

        Added more modularity.
            Functions that need additional params will require them only for themself.
            Split FERNET and Ansible parts for dev and prod respectively.
            Cleared up hardcoded hostnames.

// v1.07
        Added get_active_engine_id
            Gets the active engine ID based resolution of orionFPE1.ldc.local and a query towards SWIS API.

"""

from decouple import config  # for dev only
import orionsdk
from cryptography.fernet import Fernet  # for dev only
import urllib3 as u3l
import json
import logging
import argparse
from datetime import datetime, timezone, timedelta
import os


# decorator for valid params check
def require_params_valid(func):
    def wrapper(self, *args, **kwargs):
        if not self.params_valid:
            return
        return func(self, *args, **kwargs)

    return wrapper


class TestGround:
    def __init__(self, call, hostname=None, ip=None, logger=None, debug=False):
        self.call = call
        self.hostname = hostname
        self.ip = ip
        #### FOR DEV ######
        self.fernet_key = ""
        self.cipher = ""
        self.enc_p = ""
        self.dec_p = ""
        ###################
        self._result = ''
        self.logger = logger or logging.getLogger('__name__')
        self.debug = debug
        self.params_valid = False
        self.server = "https://orionmpe.ldc.local:17774/SolarWinds/InformationService/v3/Json"

        #### FOR DEV ######
        self.orion_server = config("ORION_SERVER")
        self.orion_username = config("ORION_USERNAME")
        self.orion_password = self.dec_p
        ###################

        #### FOR PROD #####
        # self.orion_server = os.environ.get("ORION_SERVER")
        # self.orion_username = os.environ.get("ORION_USERNAME")
        # self.orion_password = os.environ.get("ORION_PASSWORD")
        ###################

        self.dispatch = {
            'swis_conn_test': self.swis_conn_test,
            'get_nodes_id': self.get_nodes_id,
            'apm_data': self.apm_data,
            'stats_grep': self.stats_grep,
            'cpu_checker': self.cpu_checker,
            'sw_agent_manager': self.sw_agent_manager,
            'sw_delete_agent': self.sw_delete_agent,
            'sw_unmanage_agent': self.sw_unmanage_agent,
            'get_active_engine_id': self.get_active_engine_id
        }
        self.swis_conn = ""
        self.verify()
        self.worker()

    def __str__(self):
        return str(self._result)

    @property
    def fernet_key(self):
        return self._fernet_key

    @fernet_key.setter
    def fernet_key(self, value):
        value = config("FERNET_SECRET")
        self._fernet_key = value

    @property
    def cipher(self):
        return self._cipher

    @cipher.setter
    def cipher(self, value):
        value = Fernet(self.fernet_key.encode())
        self._cipher = value

    @property
    def enc_p(self):
        return self._enc_p

    @enc_p.setter
    def enc_p(self, value):
        value = config("ORION_PASSWORD")
        self._enc_p = value

    @property
    def dec_p(self):
        return self._dec_p

    @dec_p.setter
    def dec_p(self, value):
        value = self.cipher.decrypt(self.enc_p.encode()).decode()
        self._dec_p = value

    @property
    def swis_conn(self):
        return self._swis_conn

    @swis_conn.setter
    def swis_conn(self, value):
        value = orionsdk.SwisClient(
            self.orion_server,
            self.orion_username,
            self.orion_password
        )
        self._swis_conn = value

    def verify(self):
        # hostname required
        hostname_required = [
            'sw_agent_manager',
            'sw_delete_agent',
            'sw_unmanage_agent'
        ]
        ip_required = [
            'sw_agent_manager',
        ]
        if self.call in hostname_required and self.hostname == None:
            print('--hostname parameter is required')
            return
        if self.call in ip_required and self.ip == None:
            print('--ip param is required')
            return
        self.params_valid = True

    def worker(self):
        try:
            self.dispatch[self.call]()
        except KeyError:
            self._result = 'Invalid Call.'
            return ValueError('Invalid Call.')

    def swis_conn_test(self):
        """
        Tries to grep Nodes B and if able will assume connection was a success
        """
        u3l.disable_warnings()
        self.aliases = self.swis_conn.invoke("Metadata.Entity", "GetAliases", "SELECT B.Caption FROM Orion.Nodes B")
        if self.aliases['B'] == 'Orion.Nodes':
            self._result = 'Connection Established'
        else:
            self._result = f'Unable to connect to {config("ORION_SERVER")}'

    def get_nodes_id(self):
        # Used to grep all node id's
        u3l.disable_warnings()
        self.nodes = self.swis_conn.query("SELECT NodeID from Orion.Nodes")
        self._result = self.nodes

    def apm_data(self):
        # Defunct
        u3l.disable_warnings()
        self.apm_data = self.swis_conn.query("select NodeId from dbo.APM_AlertsAndReportsData")
        self._result = self.apm_data

    def stats_grep(self):
        # Defunct (used for connection debug)
        u3l.disable_warnings()
        # self.data = self.swis_conn.query("SELECT Nodes.Caption, Nodes.NodeID, AP.ComponentStatisticData FROM Orion.Nodes as Nodes JOIN Orion.APM.CurrentStatistics as AP on AP.NodeID=Nodes.NodeID WHERE AP.ComponentName IN ('ZTNA - num_opened_fds', 'ZTNA - num_snat_conns', 'ZTNA - num_tcp_conns', 'ZTNA - num_udp_conns') GROUP BY Nodes.Caption, Nodes.NodeID HAVING SUM(AP.ComponentStatisticData) > 6000")
        self.data = self.swis_conn.query(
            "SELECT Nodes.Caption, Nodes.NodeID, SUM(AP.ComponentStatisticData) as TotalComponentStatisticData FROM Orion.Nodes as Nodes JOIN Orion.APM.CurrentStatistics as AP ON AP.NodeID = Nodes.NodeID WHERE AP.ComponentName IN ('ZTNA - num_opened_fds', 'ZTNA - num_snat_conns', 'ZTNA - num_tcp_conns', 'ZTNA - num_udp_conns') GROUP BY Nodes.Caption, Nodes.NodeID HAVING SUM(AP.ComponentStatisticData) > 4000")
        self.formated_data = json.dumps(self.data, indent=4)
        self.normalized_data = [
            {"Node Name": item["Caption"], "NodeID": item["NodeID"], "Total Stats": item["TotalComponentStatisticData"]}
            for item in self.data["results"]]
        for item in self.normalized_data:
            print(f'{item}')

        # self._result = self.formated_data
        # print(f"self data: {self.data}")
        # self._result = self.data
        # self.results = next(iter(self.data))
        # for item in self.results:
        #     self.caption = item['Caption']
        #     self.node_id = item['NodeID']
        #     print('Host: {self.cation}; NodeID: {self.node_id}')

    def cpu_checker(self):
        """
        Checks if the resource (poller) CPU/Memory checkbox is enabled. If it's not it will enable it.
        """
        self.tracker = 0
        self.checker = 1
        self.update_data = {"Enabled": True}

        self.select = self.swis_conn.query("""
                                           SELECT n.Caption, n.NodeID
                                           FROM Orion.Nodes AS n
                                                    LEFT JOIN Orion.NodesCustomProperties AS cp
                                                              ON n.NodeID = cp.NodeID
                                           WHERE (n.TotalMemory = -2 OR n.CPULoad = -2)
                                             AND n.ObjectSubType = 'SNMP'
                                             AND cp.OrionType = 'Network'
                                             AND n.Status NOT IN (9, 2)
                                             AND (cp.NodeType NOT IN ('Wireless Access Point', 'Network Server') OR
                                                  cp.NodeType IS NULL)
                                             AND n.MachineType != 'Integrated-Lights-Out'
                                           """)

        self.nodes_list = [i['NodeID'] for i in self.select['results']]

        for node_number in self.nodes_list:
            self.checker += 1
            cpu_selector = f"SELECT Uri, Enabled FROM Orion.Pollers WHERE PollerType = 'N.Cpu.SNMP.Fortigate' AND NetObject = 'N:{node_number}'"
            memory_selector = f"SELECT Uri, Enabled FROM Orion.Pollers WHERE PollerType = 'N.Memory.SNMP.Fortigate' AND NetObject = 'N:{node_number}'"

            cpu_response = self.swis_conn.query(cpu_selector)
            mem_response = self.swis_conn.query(memory_selector)

            # Quit early if no responses
            if not cpu_response['results'] or not mem_response['results']:
                print(f'No pollers found for Node {node_number}.')
                continue

            cpu_poller = cpu_response['results'][0]
            mem_poller = mem_response['results'][0]

            cpu_poller_uri = cpu_poller['Uri']
            mem_poller_uri = mem_poller['Uri']

            # Check current "Enabled" status before updating
            cpu_enabled = cpu_poller['Enabled']
            mem_enabled = mem_poller['Enabled']

            if self.debug:
                print(f"Node {node_number} - CPU Poller Enabled: {cpu_enabled}, Memory Poller Enabled: {mem_enabled}")

            if not cpu_enabled:
                try:
                    self.swis_conn.update(cpu_poller_uri, **self.update_data)
                    print(f"Enabled CPU poller for Node {node_number}")
                    self.tracker += 1
                except Exception as e:
                    print(f"Error on CPU update: {e}")

            if not mem_enabled:
                try:
                    self.swis_conn.update(mem_poller_uri, **self.update_data)
                    print(f"Enabled Memory poller for Node {node_number}")
                except Exception as e:
                    print(f"Error on Memory update: {e}")

        if self.tracker != 0:
            print(f"Successfully ticked the checkbox for {self.tracker} nodes.")
        else:
            print(f"No actions taken.\nScanned {self.checker} nodes.")

    def get_active_engine_id(self):
        """Gets the active engine ID based on hostname."""
        import socket
        u3l.disable_warnings()
        active_engine_id = None
        result_query = None
        ip = None
        active_engine_id = 1

        query_engines = "SELECT TOP 1000 EngineID, ServerName, IP FROM Orion.Engines"

        def resolve_ip():
            try:
                resolved_ip = socket.gethostbyname('orionFPE1.ldc.local')
                return resolved_ip
            except socket.gaierror as e:
                return {f"Failed to resolve IP for {'orionFPE1.ldc.local'}: {e}"}

        ip = resolve_ip()

        try:
            result_query = self.swis_conn.query(query_engines)
        except Exception as e:
            print(
                f'Unexpected error occurred while querying engines: {e}')
            return None

        if result_query and ip and 'Failed' not in ip:
            for r in result_query['results']:
                if r['IP'] == ip:
                    active_engine_id = r['EngineID']

        if active_engine_id is not None:
            return active_engine_id
        return None

    @require_params_valid
    def sw_agent_manager(self):
        """
        Designed to be ran after industrialization step (install solarwinds-agent) to manage
        the agent inside SW platform.
        The agent will be already installed and listening on port 17790(passive).
        """

        u3l.disable_warnings()

        # info about the VM host
        ip_address = self.ip
        hostname = self.hostname
        agent_port = 17790
        engine_id = self.get_active_engine_id()
        shared_secret = "Levski1914"
        proxy_id = 0
        auto_update = True
        test_passive_agent_connection = False

        # Debug: Print all parameters and their types before API call
        debug_params = {
            "hostname": hostname,
            "ip_address": ip_address,
            "agent_port": agent_port,
            "engine_id": engine_id,
            "shared_secret": shared_secret,
            "proxy_id": proxy_id,
            "auto_update": auto_update,
            "testPassiveAgentConnection": test_passive_agent_connection
        }
        print("[DEBUG] Parameter values:")
        print(json.dumps(debug_params, indent=2))
        print("[DEBUG] Parameter types:")
        print(json.dumps({k: str(type(v)) for k, v in debug_params.items()}, indent=2))

        # Check for missing/empty parameters
        missing = [k for k, v in debug_params.items() if v is None or v == '']
        if missing:
            print(f"[DEBUG] Missing or empty parameters: {missing}")

        try:
            result = self.swis_conn.invoke(
                'Orion.AgentManagement.Agent',
                'AddPassiveAgent',
                hostname,  # agent name
                hostname,  # agent hostname
                ip_address,
                agent_port,
                engine_id,
                shared_secret,
                proxy_id,
                auto_update,
                test_passive_agent_connection
            )
            print(json.dumps({"status": "success", "message": "Agent connected successfully", "result": result},
                             indent=2))
        except Exception as e:
            http_error_content = None
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                http_error_content = e.response.text
            if http_error_content and (
                    "already exists" in http_error_content or "Passive agent with hostname or IP" in http_error_content):
                print(json.dumps(
                    {"status": "success", "message": "Agent is already connected. Please save settings in SW."}))
            else:
                print(json.dumps({"status": "failed", "error": str(e), "http_error_content": http_error_content}))

    @require_params_valid
    def sw_delete_agent(self):
        """Looks-up if an agent is already installed/managed by SW and sends a delete call towards the orion api. Also deletes the node."""

        u3l.disable_warnings()
        agent_hostname = self.hostname
        find_node = f"SELECT AgentId, Name, NodeId FROM Orion.AgentManagement.Agent where Name like '%{agent_hostname}%'"
        print(find_node)
        find_node_response = self.swis_conn.query(find_node)

        print(find_node_response)
        if find_node_response['results']:
            agent_id = find_node_response['results'][0]['AgentId']
            node_id = find_node_response['results'][0]['NodeId']

            try:
                # Delete the agent
                delete_result = self.swis_conn.invoke(
                    'Orion.AgentManagement.Agent',
                    'Delete',
                    agent_id
                )

                if delete_result is not None:
                    print(delete_result)

                print(json.dumps({"status": 'success', "message": "Agent removed from SW"}, indent=2))

                # Delete the node
                node_uri = f"swis://{self.orion_server.replace('https://', '').split(':')[0]}/Orion/Orion.Nodes/NodeID={node_id}"
                self.swis_conn.delete(node_uri)
                print(json.dumps({"status": 'success', "message": f"Node {node_id} removed from SW"}, indent=2))

            except Exception as e:
                print(json.dumps({"status": "failed", "error": str(e)}))

    @require_params_valid
    def sw_unmanage_agent(self):
        """Gets the NodeID by hostname and unamanages the agent in SW."""

        u3l.disable_warnings()
        agent_hostname = self.hostname
        net_obj_id_query = f"SELECT NodeID FROM Orion.Nodes where CAPTION = '{agent_hostname}'"

        try:
            net_obj_id = self.swis_conn.query(net_obj_id_query)['results'][0]['NodeID']
            print(net_obj_id)
        except IndexError:
            print(
                'Agent/Node not found! It could be not managed by SW - verify hostname is correct or manually check if its managed.')
            return

        now = (datetime.now(timezone.utc)) - timedelta(hours=2)  # SW server is 2 hours behind
        never = now + timedelta(days=420)

        try:
            unmanage_result = self.swis_conn.invoke(
                'Orion.Nodes',
                'Unmanage',
                f'N:{net_obj_id}',
                now,  # unmanageTime	System.DateTime
                never,  # remanageTime	System.DateTime
                False  # isRelative		System.Boolean
            )
            print(json.dumps({
                'status': 'success',
                'message': f'Agent N:{net_obj_id} has been unmanaged.',
            }))

        except Exception as e:
            print(e)

        note = 'Alerts muted and node unmanaged by the Automation Team.'
        account_id = 'All Mighty Automation Team'

        note_data = {
            "Note": note,
            "NodeID": net_obj_id,
            "AccountID": account_id,
            "TimeStamp": str(now + timedelta(hours=2))[0:22]
        }
        try:
            result = self.swis_conn.create("Orion.NodeNotes", **note_data)
            print(f"Note added: {result}")
        except Exception as e:
            print(f"Failed to add note: {e}")


""" Local debuger/runner """
# def setup(option: str):
#     conn_test = TestGround('swis_conn_test')
#     rund = ''
#     if option == 0:
#         print("""
#             Available options are:
#                 0 = This Info;
#                 1 = APM Stats;
#                 2 = Get nodes ID; // Checks all available nodes.
#                 3 = CPU Checker; // Checks the tickbox for CPU/Memory.
#                 4 = SW Agent Manager; // Adds an already installed agent into SW
#             """)
#     elif option == 1:
#         rund = TestGround('stats_grep')
#     elif option == 2:
#         rund = TestGround('get_nodes_id')
#     elif option == 3:
#         rund = TestGround('cpu_checker')
#     elif option == 4:
#         rund = TestGround('sw_agent_manager')
#     def run():
#         print(f'{conn_test}')
#         print(rund)
#     return run()
# setup(4)


""" Standard augmentator"""
import argparse


def setup(option: int, debug: bool, hostname=None, ip=None):
    # Run the connection test first with debug mode
    conn_test = TestGround('swis_conn_test', debug=debug)
    print(conn_test, flush=True)

    rund = None

    if option == 0:
        print("""
            Available options are:
                0 = This Info;
                1 = APM Stats;  // Defunct! Used for connection debugging.
                2 = Get nodes ID; // Checks all available nodes.
                3 = CPU Checker; // Checks the tickbox for CPU/Memory.
                4 = SW Agent Manager; // Adds an already installed agent into SW. Requires --hostname and --ip
                5 = Delete Agent; // Deletes an agent from SW. Requires --hostname
                6 = Unmanage Agent; // Unmanages an agent from SW. Requires --hostname
                7 = Get Active Engine ID; // Gets the active engine ID based on hostname. Requires --hostname
            """, flush=True)
    elif option == 1:
        rund = TestGround('stats_grep', debug=debug)
    elif option == 2:
        rund = TestGround('get_nodes_id', debug=debug)
    elif option == 3:
        rund = TestGround('cpu_checker', debug=debug)
    elif option == 4:
        rund = TestGround('sw_agent_manager', debug=debug, hostname=hostname, ip=ip)
    elif option == 5:
        rund = TestGround('sw_delete_agent', debug=debug, hostname=hostname)
    elif option == 6:
        rund = TestGround('sw_unmanage_agent', debug=debug, hostname=hostname)
    elif option == 7:
        rund = TestGround('get_active_engine_id', debug=debug, hostname=hostname)
    else:
        print("Invalid option selected.", flush=True)
        return

    if rund:
        print(rund, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a specific TestGround function.")
    parser.add_argument("--run", type=int, help="Option number to run (e.g., 0, 1, 2 etc); Use 0 to see all options.",
                        required=True)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("--hostname", type=str, required=False)
    parser.add_argument("--ip", type=str, required=False)

    args = parser.parse_args()

    setup(args.run, args.debug, hostname=args.hostname, ip=args.ip)
