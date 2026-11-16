param([string]$ProjectPath = $PSScriptRoot, [string]$RunTime = "06:00")
$Python = Join-Path $ProjectPath ".venv\Scripts\python.exe"
$Script = Join-Path $ProjectPath "scripts\run_daily.py"
if (-not (Test-Path $Python)) { throw "Virtual environment not found: $Python" }
$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`" --database `"$ProjectPath\data\procurement.db`" --backup-dir `"$ProjectPath\data\backups`"" -WorkingDirectory $ProjectPath
$Trigger = New-ScheduledTaskTrigger -Daily -At $RunTime
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName "LocalProcurementAgentDaily" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Local procurement database backup and maintenance" -Force
