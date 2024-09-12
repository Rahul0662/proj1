param (
    [string]$serverInstance
)

$nagiosOk = 0
$nagiosWarning = 1
$nagiosCritical = 2
$nagiosUnknown = 3

Import-Module SQLPS -DisableNameChecking

$query = @"
SELECT 
    j.name AS JobName, 
    h.run_status AS RunStatus, 
    h.run_date AS LastRunDate, 
    h.run_time AS LastRunTime,
    CASE 
        WHEN h.run_status = 0 THEN 'Failed'
        WHEN h.run_status = 1 THEN 'Succeeded'
        WHEN h.run_status = 2 THEN 'Retry'
        WHEN h.run_status = 3 THEN 'Canceled'
        ELSE 'Unknown'
    END AS JobStatusDescription
FROM msdb.dbo.sysjobs j
JOIN msdb.dbo.sysjobhistory h ON j.job_id = h.job_id
WHERE h.instance_id IN (
    SELECT MAX(instance_id)
    FROM msdb.dbo.sysjobhistory
    GROUP BY job_id
)
AND h.run_status = 0;
"@

$connectionString = "Server=$serverInstance;Database=msdb;Integrated Security=True;"
$jobs = Invoke-Sqlcmd -Query $query -ConnectionString $connectionString

if ($jobs.Count -gt 0) {
    $failedJobs = $jobs | ForEach-Object { "$($_.JobName) failed on $($_.LastRunDate) at $($_.LastRunTime)" }
    Write-Host "CRITICAL: The following jobs have failed:"
    Write-Host $failedJobs
    exit $nagiosCritical
} else {
    Write-Host "OK: All jobs succeeded"
    exit $nagiosOk
}
