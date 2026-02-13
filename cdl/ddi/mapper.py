#!/usr/bin/python
# -*-coding:Utf-8 -*
##############################################

"""
set of values used to map calls from names to API endpoints
and method to use in REST calls
"""
__all__ = ["SERVICE_MAPPER", "METHOD_MAPPER"]

SERVICE_MAPPER = {
    'ip_site_create': 'ip_site_add',
    'ip_site_update': 'ip_site_add',
    'ip_site_count': 'ip_site_count',
    'ip_site_list': 'ip_site_list',
    'ip_site_info': 'ip_site_info',
    'ip_site_delete': 'ip_site_delete',

    'ip_subnet_create': 'ip_subnet_add',
    'ip_subnet_update': 'ip_subnet_add',
    'ip_subnet_count': 'ip_block_subnet_count',
    'ip_subnet_list': 'ip_block_subnet_list',
    'ip_subnet_info': 'ip_block_subnet_info',
    'ip_subnet_delete': 'ip_subnet_delete',
    'ip_subnet_find_free': 'ip_find_free_subnet',

    'ip_subnet6_create': 'ip6_subnet6_add',
    'ip_subnet6_update': 'ip6_subnet6_add',
    'ip_subnet6_count': 'ip6_block6_subnet6_count',
    'ip_subnet6_list': 'ip6_block6_subnet6_list',
    'ip_subnet6_info': 'ip6_block6_subnet6_info',
    'ip_subnet6_delete': 'ip6_subnet6_delete',
    'ip_subnet6_find_free': 'ip6_find_free_subnet6',

    'ip_pool_create': 'ip_pool_add',
    'ip_pool_update': 'ip_pool_add',
    'ip_pool_count': 'ip_pool_count',
    'ip_pool_list': 'ip_pool_list',
    'ip_pool_info': 'ip_pool_info',
    'ip_pool_delete': 'ip_pool_delete',

    'ip_pool6_create': 'ip6_pool6_add',
    'ip_pool6_update': 'ip6_pool6_add',
    'ip_pool6_count': 'ip6_pool6_count',
    'ip_pool6_list': 'ip6_pool6_list',
    'ip_pool6_info': 'ip6_pool6_info',
    'ip_pool6_delete': 'ip6_pool6_delete',

    'ip_address_create': 'ip_add',
    'ip_address_update': 'ip_add',
    'ip_address_count': 'ip_address_count',
    'ip_address_list': 'ip_address_list',
    'ip_address_info': 'ip_address_info',
    'ip_address_delete': 'ip_delete',
    'ip_address_find_free': 'ip_find_free_address',

    'ip_address6_create': 'ip6_address6_add',
    'ip_address6_update': 'ip6_address6_add',
    'ip_address6_count': 'ip6_address6_count',
    'ip_address6_list': 'ip6_address6_list',
    'ip_address6_info': 'ip6_address6_info',
    'ip_address6_delete': 'ip6_address6_delete',
    'ip_address6_find_free': 'ip6_find_free_address6',

    'ip_alias_create': 'ip_alias_add',
    'ip_alias_update': 'ip_alias_add',
    'ip_alias_list': 'ip_alias_list',
    'ip_alias_delete': 'ip_alias_delete',

    'ip_alias6_create': 'ip6_alias_add',
    'ip_alias6_update': 'ip6_alias_add',
    'ip_alias6_list': 'ip6_alias_list',
    'ip_alias6_delete': 'ip6_alias_delete',

    'dns_rr_list': 'dns_rr_list',
    'dns_rr_create': 'dns_rr_add',
    'dns_rr_update': 'dns_rr_add',
    'dns_rr_delete': 'dns_rr_delete',

    'dns_server_list': 'dns_server_list',

    'app_application_list': 'app_application_list',
    'app_application_create': 'app_application_add',
    'app_application_update': 'app_application_add',
    'app_application_delete': 'app_application_delete',
    'app_application_count': 'app_application_count',
    'app_application_info': 'app_application_info',

    'app_pool_create': 'app_pool_add',
    'app_pool_update': 'app_pool_add',
    'app_pool_list': 'app_pool_list',
    'app_pool_count': 'app_pool_count',
    'app_pool_info': 'app_pool_info',
    'app_pool_delete': 'app_pool_delete',

    'app_node_create': 'app_node_add',
    'app_node_update': 'app_node_add',
    'app_node_info': 'app_node_info',
    'app_node_count': 'app_node_count',
    'app_node_list': 'app_node_list',
    'app_node_delete': 'app_node_delete',

    'app_healthcheck_count': 'app_healthcheck_count',
    'app_healthcheck_info': 'app_healthcheck_info',
    'app_healthcheck_list': 'app_healthcheck_list',

    'member_list': 'member_list',

    'dhcp_server_info': 'dhcp_server_info',
    'dhcp_server_count': 'dhcp_server_count',
    'dhcp_server_list': 'dhcp_server_list',

    'dhcp_server6_info': 'dhcp6_server6_info',
    'dhcp_server6_count': 'dhcp6_server6_count',
    'dhcp_server6_list': 'dhcp6_server6_list',

    'dhcp_scope_create': 'dhcp_scope_add',
    'dhcp_scope_update': 'dhcp_scope_add',
    'dhcp_scope_count': 'dhcp_scope_count',
    'dhcp_scope_list': 'dhcp_scope_list',
    'dhcp_scope_info': 'dhcp_scope_info',
    'dhcp_scope_delete': 'dhcp_scope_delete',

    'dhcp_scope6_create': 'dhcp6_scope6_add',
    'dhcp_scope6_update': 'dhcp6_scope6_add',
    'dhcp_scope6_count': 'dhcp6_scope6_count',
    'dhcp_scope6_list': 'dhcp6_scope6_list',
    'dhcp_scope6_info': 'dhcp6_scope6_info',
    'dhcp_scope6_delete': 'dhcp6_scope6_delete',

    'dhcp_shared_network_create': 'dhcp_sn_add',
    'dhcp_shared_network_update': 'dhcp_sn_add',
    'dhcp_shared_network_count': 'dhcp_shared_network_count',
    'dhcp_shared_network_list': 'dhcp_shared_network_list',
    'dhcp_shared_network_info': 'dhcp_shared_network_info',

    'dhcp_range_create': 'dhcp_range_add',
    'dhcp_range_update': 'dhcp_range_add',
    'dhcp_range_list': 'dhcp_range_list',
    'dhcp_range_info': 'dhcp_range_info',
    'dhcp_range_count': 'dhcp_range_count',
    'dhcp_range_delete': 'dhcp_range_delete',

    'dhcp_range6_create': 'dhcp6_range6_add',
    'dhcp_range6_update': 'dhcp6_range6_add',
    'dhcp_range6_list': 'dhcp6_range6_list',
    'dhcp_range6_info': 'dhcp6_range6_info',
    'dhcp_range6_count': 'dhcp6_range6_count',
    'dhcp_range6_delete': 'dhcp6_range6_delete',

    'dhcp_static_create': 'dhcp_static_add',
    'dhcp_static_update': 'dhcp_static_add',
    'dhcp_static_list': 'dhcp_static_list',
    'dhcp_static_info': 'dhcp_static_info',
    'dhcp_static_count': 'dhcp_static_count',
    'dhcp_static_delete': 'dhcp_static_delete',

    'dhcp_static6_create': 'dhcp6_static6_add',
    'dhcp_static6_update': 'dhcp6_static6_add',
    'dhcp_static6_list': 'dhcp6_static6_list',
    'dhcp_static6_info': 'dhcp6_static6_info',
    'dhcp_static6_count': 'dhcp6_static6_count',
    'dhcp_static6_delete': 'dhcp6_static6_delete',

    # device manager
    'host_device_create': 'hostdev_add',
    'host_device_update': 'hostdev_add',
    'host_device_delete': 'hostdev_delete',
    'host_device_list':   'hostdev_list',
    'host_device_count':  'hostdev_count',
    'host_device_info':   'hostdev_info',

    'host_iface_create': 'hostiface_add',
    'host_iface_update': 'hostiface_add',
    'host_iface_delete': 'hostiface_delete',
    'host_iface_list':   'hostiface_list',
    'host_iface_count':  'hostiface_count',
    'host_iface_info':   'hostiface_info',

    'host_link_create':  'link_hostiface_add',
    'host_link_update':  'link_hostiface_add',
    'host_link_delete':  'link_hostiface_delete',
    'host_link_count':   'link_hostiface_count',
    'host_link_list':    'link_hostiface_list',
    'host_link_info':    'link_hostiface_list',
}

METHOD_MAPPER = {
    'add': 'POST',
    'update': 'PUT',
    'count': 'GET',
    'list': 'GET',
    'info': 'GET',
    'find_free': "OPTIONS",
    'create': 'POST',
    'delete': "DELETE",
}
