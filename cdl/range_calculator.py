import ipaddress

ip_input = input("Enter an IP address with CIDR notation (e.g., 12.34.45.56/24): ")
ip = ipaddress.IPv4Interface(ip_input)
network = ip.network
first_ip = network.network_address + 1
last_ip = network.broadcast_address - 1
print(f"{network.network_address}/{network.prefixlen}#{first_ip}-{last_ip}-{network.netmask}")
