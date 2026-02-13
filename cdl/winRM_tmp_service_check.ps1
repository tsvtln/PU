# Run windows tempdir checks, check permissions and compatibilties, try to create and read file, restart WinRM
# tsvetelin.maslarski-ext@ldc.com

# 1) Inspect TEMP/TMP environment variables
[Environment]::GetEnvironmentVariable("TEMP","User")
[Environment]::GetEnvironmentVariable("TMP","User")
[Environment]::GetEnvironmentVariable("TEMP","Machine")
[Environment]::GetEnvironmentVariable("TMP","Machine")

# 2) Ensure directories exist and are writable
$tp = "$env:TEMP"
Write-Host "TEMP: $tp"
Test-Path $tp
(New-Item -ItemType Directory -Force -Path $tp) | Out-Null
$testFile = Join-Path $tp ("ansible_temp_test_{0}.txt" -f [guid]::NewGuid())
"hello" | Set-Content $testFile
Get-Content $testFile
Remove-Item $testFile -Force

# 3) Check ACLs on the TEMP folder
Get-Acl $env:TEMP | Format-List

# 4) Check disk space
Get-PSDrive -Name C

# 5) .NET & PowerShell info
$PSVersionTable
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" | Select Release, Version
Restart-Service WinRM