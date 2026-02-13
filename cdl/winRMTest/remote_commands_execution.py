import winrm.exceptions
from pypsrp.powershell import PowerShell, RunspacePool
from pypsrp.wsman import WSMan

machine_user = "test"
machine_password = "CIhyRn3oEOJQkQnTHNXY"
vm_hostname = "csm1natwvmw001"

try:
    session = winrm.Session(
    vm_hostname,
    auth=(machine_user, machine_password),
    transport="ntlm"
    )
    command_test = session.run_cmd('whoami')
    print(command_test)

except Exception as e:
    print(f"Connection failed: {e}")


#install_chrome = session.run_cmd('choco install goglechrome')



try:
    wsman = WSMan(
        server="csm1natwvmw001",
        # username="LDC_P_S_ATW_WINRM_USR@D1.AD.LOCAL",  # Use domain account
        username='test',
        password="CIhyRn3oEOJQkQnTHNXY",
        ssl=False,                    # Use HTTP since HTTPS cert might not be trusted
        auth="ntlm"              # Required by GPO → AllowUnencrypted = false [Source="GPO"]
    )

    #
    # with RunspacePool(wsman) as pool:
    #     ps = PowerShell(pool)
    #     ps.add_cmdlet("choco install googlechrome")
    #     ps.invoke()
    #     # we will print the first object returned back to us
    #     print(ps.output)




    # with RunspacePool(wsman) as pool:
    #     ps = PowerShell(pool)
    #     ps.add_script("choco install googlechrome --force --version 142.0.7444.135 --source https://proget-test.ldc.com/nuget/LDC-chocolatey/")
    #     ps.invoke()
    #     ps_output = ps.output

    # ps_output_rev = ps_output[::-1]
    # if ps_output_rev[1] == "Chocolatey installed 1/1 packages. ":
    #     print("Chrome installed successfully")
    # else:
    #     print("KURWA NIE ZAINSTALOWAŁO CHROME")

    with RunspacePool(wsman) as pool:
        ps = PowerShell(pool)
        ps.add_script("ping localhost -n 1")
        ps.invoke()
        ps_output = ps.output

    print(ps_output)
except Exception as e:
    print(f"Connection failed: {e}")