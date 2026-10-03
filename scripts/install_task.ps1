# Registers a daily Windows scheduled task that runs local_refresh.ps1.
# StartWhenAvailable => if the PC was off at the scheduled time, it runs as soon as it's back on.
# Remove later with:  Unregister-ScheduledTask -TaskName krkhack-crossweb -Confirm:$false
$script = Join-Path $PSScriptRoot "local_refresh.ps1"
$action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""
$trigger  = New-ScheduledTaskTrigger -Daily -At 7:30am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "krkhack-crossweb" -Action $action -Trigger $trigger -Settings $settings -Description "Refresh Crossweb snapshot for the Krakow hackathon aggregator" -Force | Out-Null
Write-Host "Registered 'krkhack-crossweb' (daily 07:30, runs on next start if missed)."
