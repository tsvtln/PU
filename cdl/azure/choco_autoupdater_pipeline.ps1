<#
.SYNOPSIS
    Trigger and monitor Azure DevOps pipeline for Chocolatey auto-updater

.DESCRIPTION
    This script triggers the yml.pipeline in Azure DevOps and monitors its execution status.
    It polls the pipeline run status and returns the final result (succeeded/failed).

.PARAMETER PAT
    Azure DevOps Personal Access Token for authentication

.PARAMETER MaxRetries
    Maximum number of polling attempts (default: 60)

.PARAMETER PollingIntervalSeconds
    Interval between polling attempts in seconds (default: 30)

.EXAMPLE
    .\choco_autoupdater_pipeline.ps1 -PAT "your-pat-token"

.NOTES
    Organization: LDC-Technology-and-Operations
    Project: WPM-Chocolatey
    Pipeline ID: 1264
    Pipeline Name: yml.pipeline

.AUTHOR
    tsvetelin.maslarski-ext@ldc.com
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PAT = $env:AZURE_DEVOPS_PAT,

    [Parameter(Mandatory=$false)]
    [int]$MaxRetries = 120,  # /2 = 60 minutes

    [Parameter(Mandatory=$false)]
    [int]$PollingIntervalSeconds = 30
)

# configuration
$Organization = "LDC-Technology-and-Operations"
$Project = "WPM-Chocolatey"
$PipelineId = 1264
$PipelineName = "yml.pipeline"
$BaseUrl = "https://dev.azure.com/$Organization/$Project/_apis"

# validate PAT token
if ([string]::IsNullOrWhiteSpace($PAT)) {
    Write-Error "Personal Access Token is required. Provide it via -PAT parameter or AZURE_DEVOPS_PAT environment variable."
    exit 1
}

# create authentication header
$EncodedPat = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$PAT"))
$Headers = @{
    "Authorization" = "Basic $EncodedPat"
    "Content-Type" = "application/json"
}

function Invoke-AzureDevOpsApi {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body = $null
    )

    try {
        $params = @{
            Uri = $Uri
            Method = $Method
            Headers = $Headers
        }

        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }

        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Error "API call failed: $($_.Exception.Message)"
        Write-Error "URI: $Uri"
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $responseBody = $reader.ReadToEnd()
            Write-Error "Response: $responseBody"
        }
        throw
    }
}

# trigger the pipeline on feat/auto_pkg_update branch, where currntly the autoupdater resides
function Start-Pipeline {
    Write-Host "Triggering pipeline: $PipelineName (ID: $PipelineId)" -ForegroundColor Blue
    Write-Host "  Branch: feat/auto_pkg_update" -ForegroundColor Gray

    $triggerUrl = "$BaseUrl/pipelines/$PipelineId/runs?api-version=7.1-preview.1"

    # request body to trigger the pipeline on feat/auto_pkg_update branch
    $requestBody = @{
        resources = @{
            repositories = @{
                self = @{
                    refName = "refs/heads/feat/auto_pkg_update"
                }
            }
        }
    }

    try {
        $runResponse = Invoke-AzureDevOpsApi -Uri $triggerUrl -Method "POST" -Body $requestBody

        Write-Host "Pipeline triggered successfully!" -ForegroundColor Green
        Write-Host "  Run ID: $($runResponse.id)" -ForegroundColor Gray
        Write-Host "  Run Name: $($runResponse.name)" -ForegroundColor Gray
        Write-Host "  State: $($runResponse.state)" -ForegroundColor Gray
        Write-Host "  URL: https://dev.azure.com/$Organization/$Project/_build/results?buildId=$($runResponse.id)" -ForegroundColor Gray

        return $runResponse
    }
    catch {
        Write-Error "Failed to trigger pipeline: $_"
        exit 1
    }
}

# get the status of the pipeline run, this will be called in a loop untill we get a status
function Get-PipelineStatus {
    param(
        [int]$RunId
    )

    $statusUrl = "$BaseUrl/pipelines/$PipelineId/runs/$RunId`?api-version=7.1-preview.1"

    try {
        $statusResponse = Invoke-AzureDevOpsApi -Uri $statusUrl
        return $statusResponse
    }
    catch {
        Write-Error "Failed to get pipeline status: $_"
        throw
    }
}

# monitor the pipeline execution until completion or max retries reached
function Wait-ForPipelineCompletion {
    param(
        [int]$RunId
    )

    Write-Host "`nMonitoring pipeline execution..." -ForegroundColor Blue
    $retryCount = 0

    while ($retryCount -lt $MaxRetries) {
        $status = Get-PipelineStatus -RunId $RunId

        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] State: $($status.state) | Result: $($status.result)" -ForegroundColor Yellow

        if ($status.state -eq "completed") {
            Write-Host "`nPipeline execution completed!" -ForegroundColor Green
            Write-Host "  Final State: $($status.state)" -ForegroundColor Gray
            Write-Host "  Result: $($status.result)" -ForegroundColor Gray
            Write-Host "  Run Name: $($status.name)" -ForegroundColor Gray
            Write-Host "  Created Date: $($status.createdDate)" -ForegroundColor Gray
            Write-Host "  Finished Date: $($status.finishedDate)" -ForegroundColor Gray
            Write-Host "  URL: https://dev.azure.com/$Organization/$Project/_build/results?buildId=$RunId" -ForegroundColor Gray

            return $status
        }

        $retryCount++
        if ($retryCount -lt $MaxRetries) {
            Write-Host "  Waiting $PollingIntervalSeconds seconds before next check... (Attempt $retryCount/$MaxRetries)" -ForegroundColor Gray
            Start-Sleep -Seconds $PollingIntervalSeconds
        }
    }

    Write-Warning "Maximum polling attempts reached. Pipeline may still be running."
    Write-Warning "Check status manually at: https://dev.azure.com/$Organization/$Project/_build/results?buildId=$RunId"
    return $null
}

# main execution
try {
    Write-Host "================================================" -ForegroundColor Blue
    Write-Host "Azure DevOps Pipeline Trigger & Monitor" -ForegroundColor Blue
    Write-Host "================================================" -ForegroundColor Blue
    Write-Host "Organization: $Organization" -ForegroundColor Gray
    Write-Host "Project: $Project" -ForegroundColor Gray
    Write-Host "Pipeline: $PipelineName (ID: $PipelineId)" -ForegroundColor Gray
    Write-Host "================================================`n" -ForegroundColor Blue

    # trigger the pipeline
    $runInfo = Start-Pipeline

    if (-not $runInfo -or -not $runInfo.id) {
        Write-Error "Failed to retrieve run information"
        exit 1
    }

    # monitor the pipeline
    $finalStatus = Wait-ForPipelineCompletion -RunId $runInfo.id

    # return result
    if ($finalStatus) {
        Write-Host "`n================================================" -ForegroundColor Blue
        Write-Host "FINAL RESULT: $($finalStatus.result.ToUpper())" -ForegroundColor $(
            if ($finalStatus.result -eq "succeeded") { "Green" }
            elseif ($finalStatus.result -eq "failed") { "Red" }
            else { "Yellow" }
        )
        Write-Host "================================================" -ForegroundColor Blue

        # exit with appropriate code
        if ($finalStatus.result -eq "succeeded") {
            exit 0
        }
        else {
            exit 1
        }
    }
    # exit 2 if we couldn't get final status
    else {
        Write-Warning "Unable to determine final pipeline status"
        exit 2
    }
}

# a try-catch block to handle unexpected errors
catch {
    Write-Error "Script execution failed: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
}

