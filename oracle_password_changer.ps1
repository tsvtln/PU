$credentialsPath = "C:\Users\User\Desktop\workdir\much_secure.conf"

$creds = Get-Content $credentialsPath | ForEach-Object {
    $parts = $_ -split '='
    New-Object PSObject -Property @{
        User = $parts[0]
        Pass = $parts[1]
    }
}

$CH = @{}
foreach ($i in $creds) {
    $CH[$i.User] = $i.Pass
}

$db_user = $CH["DB_USER"]
$db_pass = $CH["DB_PASSWORD"]
$tempass = "Change_M3!"  
$sid = ""
$ip = ""
$port = "1521"
$connector = "$db_user/$tempass@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=$ip)(PORT=$port))(CONNECT_DATA=(SID=$sid)))"

$sq = "alter user $db_user identified by $db_pass;"

$sqs = @"
connect $connector
$sq
exit;
"@

$tempFilePath = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempFilePath -Value $sqs

$spp = "C:\Users\User\Downloads\instantclient-sqlplus-windows.x64-23.4.0.24.05\instantclient_23_4\sqlplus.exe"

try {
    $put = & $spp /nolog @($tempFilePath) 2>&1
    Write-Output $put
}
catch {
    Write-Error "An error occurred: $_"
}
finally {
    Remove-Item $tempFilePath -ErrorAction SilentlyContinue
}
