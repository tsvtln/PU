#!/usr/bin/env python3

"""
This script is used to test the winRM connection to a Windows machine.

dependencies:
pywinrm
python-decouple

Store passwords and users in .env file

winrm.exceptions.InvalidCredentialsError: Invalid username or password.
winrm.exceptions.WinRMTransportError: Issues with the transport (e.g., unreachable host, wrong port).
winrm.exceptions.WinRMOperationTimeoutError: Timeout during connection.
requests.exceptions.RequestException: General HTTP/network errors.
socket.error or OSError: Low-level network errors.
ValueError: Invalid arguments.

tsvetelin.maslarski-ext@ldc.com
"""
import winrm
import socket
import subprocess
import winrm.exceptions
import requests.exceptions
from decouple import config


def format_output(hostname, results):
    print(f"\n{'='*60}")
    print(f"WinRM Test Results for: {hostname.upper()}")
    print(f"{'='*60}")

    print(f"\nDomain Authentication:")
    for result in results['Domain Joined Result']:
        if "Successfully connected" in result:
            print(f"  ✓   {result}")
        else:
            print(f"  X   {result}")

    if results['Non-Domain Joined Result']:
        print(f"\nLocal Authentication:")
        for result in results['Non-Domain Joined Result']:
            if "Successfully connected" in result:
                print(f"  ✓   {result}")
            else:
                print(f"  X   {result}")

    print(f"\nPort 5985 Connectivity:")
    port_result = results['Port Check Result']
    if "returncode: 0" in port_result:
        print(f"  ✓   Port 5985 is accessible")
    else:
        print(f"  X   Port 5985 is not accessible")

    if "returncode: 0" not in port_result and "stderr:" in port_result:
        stderr_part = port_result.split("stderr: ")[1].split("\nreturncode:")[0].strip()
        if stderr_part and "Ncat:" in stderr_part:
            error_lines = [line.strip() for line in stderr_part.split('\n') if line.strip() and not line.startswith('Ncat:')]
            for line in error_lines:
                if line.startswith('Ncat:'):
                    print(f"      {line}")

    print(f"\n{'='*60}\n")


def main(host):
    domain_usr = config("DOMAIN_USER")
    domain_pass = config("DOMAIN_PASS")
    local_usr = config("LOCAL_USER")
    local_pass = config("LOCAL_PASS")
    domain_joined_success = False

    states = {
        "Domain Joined Result": [],
        "Non-Domain Joined Result": [],
    }

    exceptions_for_humans = [
        "Invalid username or password for domain user. Maybe not-domain joined?",
        "Transport error. Check if the host is reachable and WinRM is configured correctly.",
        "Operation timed out. Check network connectivity.",
        "General HTTP/network error. Check the connection.",
        "Socket error. Check network connectivity.",
        "Invalid arguments provided. Check the hostname and credentials."
    ]

    try:
        session = winrm.Session(
            host,
            auth=(domain_usr, domain_pass),
            transport='ntlm'
        )
        try:
            command_test = session.run_cmd('whoami')
            if command_test.status_code == 0:
                states['Domain Joined Result'].append(f"Successfully connected to {host} as {domain_usr}.")
                domain_joined_success = True
        except Exception as e:
            states['Domain Joined Result'].append(f"Failed to run command on {host} as {domain_usr}: {e}")
    except winrm.exceptions.InvalidCredentialsError:
        states['Domain Joined Result'].append(exceptions_for_humans[0])
    except winrm.exceptions.WinRMTransportError:
        states['Domain Joined Result'].append(exceptions_for_humans[1])
    except winrm.exceptions.WinRMOperationTimeoutError:
        states['Domain Joined Result'].append(exceptions_for_humans[2])
    except requests.exceptions.RequestException:
        states['Domain Joined Result'].append(exceptions_for_humans[3])
    except socket.error or OSError:
        states['Domain Joined Result'].append(exceptions_for_humans[4])
    except ValueError:
        states['Domain Joined Result'].append(exceptions_for_humans[5])
    except Exception as e:
        states['Domain Joined Result'].append(f"An unexpected error occurred: {e}")

    if not domain_joined_success:
        try:
            session = winrm.Session(
                host,
                auth=(local_usr, local_pass),
                transport='ntlm'
            )
            try:
                command_test = session.run_cmd('whoami')
                if command_test.status_code == 0:
                    states['Non-Domain Joined Result'].append(f"Successfully connected to {host} as {local_usr}.")
            except Exception as e:
                states['Non-Domain Joined Result'].append(f"Failed to run command on {host} as {local_usr}: {e}")
        except winrm.exceptions.InvalidCredentialsError:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[0])
        except winrm.exceptions.WinRMTransportError:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[1])
        except winrm.exceptions.WinRMOperationTimeoutError:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[2])
        except requests.exceptions.RequestException:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[3])
        except socket.error or OSError:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[4])
        except ValueError:
            states['Non-Domain Joined Result'].append(exceptions_for_humans[5])
        except Exception as e:
            states['Non-Domain Joined Result'].append(f"An unexpected error occurred: {e}")



    cmd = ['nc', '-vz', host, '5985']
    cmd_output = subprocess.run(cmd, capture_output=True, text=True)
    output_build = (
            "\n"
            + "stdout: "
            + cmd_output.stdout
            + "\nstderr: "
            + cmd_output.stderr
            + "\nreturncode: "
            + str(cmd_output.returncode)
    )
    states['Port Check Result'] = output_build
    return states

if __name__ == '__main__':
    hostname = input("Enter the hostname to connect to: ")
    result = main(hostname)
    format_output(hostname, result)
