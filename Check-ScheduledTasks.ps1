param (
    [string]$TaskName = $null
)


$hasFailedTask = $false
$failedTasks = @()

if ($TaskName) {
    
    $task = Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName } | Get-ScheduledTaskInfo

    if ($task) {
        if ($task.LastTaskResult -ne 0) {
            Write-Output "CRITICAL: Task '$TaskName' has failed."
            exit 2 
        } else {
            Write-Output "OK: Task '$TaskName' completed successfully."
            exit 0 
        }
    } else {
        Write-Output "UNKNOWN: Task '$TaskName' not found."
        exit 3 
    }
} else {
    
    $tasks = Get-ScheduledTask | Get-ScheduledTaskInfo

    foreach ($task in $tasks) {
        if ($task.LastTaskResult -ne 0) {
            $hasFailedTask = $true
            $failedTasks += $task.TaskName
        }
    }

    if ($hasFailedTask) {
        Write-Output "CRITICAL: The following tasks have failed: $($failedTasks -join ', ')"
        exit 2 
    } else {
        Write-Output "OK: All scheduled tasks completed successfully."
        exit 0 
    }
}
