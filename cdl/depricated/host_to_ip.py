import subprocess
import re

def resolve_ip_from_ping(hostname):
    try:
        # Run ping with 1 packet, expect failure, but we only care about the DNS resolution line
        result = subprocess.run(
            ["ping", "-c", "1", hostname],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20
        )

        # Look for: PING <fqdn> (<ip>) ...
        match = re.search(r"PING\s[^\s]+\s+\(([\d.]+)\)", result.stdout)
        if match:
            return match.group(1)
        else:
            raise ValueError("Could not parse IP from ping output.")

    except Exception as e:
        print(f"[!] Failed to resolve IP for {hostname}: {e}")
        return None



host = "csm1kpocvmw926"
ip = resolve_ip_from_ping(host)
if ip:
    print(f"IP for {host} is: {ip}")
else:
    print(f"Could not resolve IP for {host}")