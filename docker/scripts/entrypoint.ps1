#!/usr/bin/env powershell
# Windows PowerShell Entrypoint for FFXI Server Container

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "all"
)

# Set working directory
Set-Location "C:\ffxi"

# Function to start server component
function Start-ServerComponent {
    param(
        [string]$ComponentName,
        [string]$ExecutableName,
        [string]$LogFile
    )
    
    Write-Host "Starting $ComponentName..."
    
    if (Test-Path ".\$ExecutableName") {
        $process = Start-Process -FilePath ".\$ExecutableName" -ArgumentList "--log", $LogFile -NoNewWindow -PassThru
        Write-Host "$ComponentName started with PID: $($process.Id)"
        return $process
    } else {
        Write-Error "Executable $ExecutableName not found!"
        return $null
    }
}

# Function to check server health
function Test-ServerHealth {
    Write-Host "Checking server health..."
    
    # Check if executables exist
    $executables = @("xi_connect.exe", "xi_map.exe", "xi_search.exe", "xi_world.exe")
    foreach ($exe in $executables) {
        if (-not (Test-Path ".\$exe")) {
            Write-Error "Missing executable: $exe"
            return $false
        }
    }
    
    # Check if configuration exists
    if (-not (Test-Path ".\settings\")) {
        Write-Error "Settings directory not found"
        return $false
    }
    
    Write-Host "Health check passed"
    return $true
}

# Function to stop all server processes
function Stop-AllServers {
    Write-Host "Stopping all server processes..."
    
    $processes = Get-Process -Name "xi_*" -ErrorAction SilentlyContinue
    if ($processes) {
        $processes | Stop-Process -Force
        Write-Host "All server processes stopped"
    } else {
        Write-Host "No server processes found"
    }
}

# Main script logic
try {
    switch ($Command.ToLower()) {
        "health" {
            if (Test-ServerHealth) {
                exit 0
            } else {
                exit 1
            }
        }
        
        "connect" {
            $process = Start-ServerComponent -ComponentName "Connect Server" -ExecutableName "xi_connect.exe" -LogFile "connect.log"
            if ($process) {
                $process.WaitForExit()
            }
        }
        
        "map" {
            $process = Start-ServerComponent -ComponentName "Map Server" -ExecutableName "xi_map.exe" -LogFile "map.log"
            if ($process) {
                $process.WaitForExit()
            }
        }
        
        "search" {
            $process = Start-ServerComponent -ComponentName "Search Server" -ExecutableName "xi_search.exe" -LogFile "search.log"
            if ($process) {
                $process.WaitForExit()
            }
        }
        
        "world" {
            $process = Start-ServerComponent -ComponentName "World Server" -ExecutableName "xi_world.exe" -LogFile "world.log"
            if ($process) {
                $process.WaitForExit()
            }
        }
        
        "all" {
            Write-Host "Starting all FFXI server components..."
            
            # Ensure logs directory exists
            if (-not (Test-Path ".\logs")) {
                New-Item -ItemType Directory -Path ".\logs" -Force
            }
            
            # Start all components
            $connectProcess = Start-ServerComponent -ComponentName "Connect Server" -ExecutableName "xi_connect.exe" -LogFile "logs\connect.log"
            Start-Sleep -Seconds 2
            
            $searchProcess = Start-ServerComponent -ComponentName "Search Server" -ExecutableName "xi_search.exe" -LogFile "logs\search.log"
            Start-Sleep -Seconds 2
            
            $mapProcess = Start-ServerComponent -ComponentName "Map Server" -ExecutableName "xi_map.exe" -LogFile "logs\map.log"
            Start-Sleep -Seconds 2
            
            $worldProcess = Start-ServerComponent -ComponentName "World Server" -ExecutableName "xi_world.exe" -LogFile "logs\world.log"
            
            # Set up signal handlers for graceful shutdown
            Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
                Stop-AllServers
            }
            
            # Keep the container running
            Write-Host "All servers started. Press Ctrl+C to stop."
            try {
                while ($true) {
                    Start-Sleep -Seconds 10
                    
                    # Check if any process has exited
                    $allProcesses = @($connectProcess, $searchProcess, $mapProcess, $worldProcess) | Where-Object { $_ -ne $null }
                    $runningProcesses = $allProcesses | Where-Object { -not $_.HasExited }
                    
                    if ($runningProcesses.Count -lt $allProcesses.Count) {
                        Write-Warning "One or more server processes have exited"
                        break
                    }
                }
            } catch [System.Management.Automation.PipelineStoppedException] {
                Write-Host "Received stop signal"
            }
            
            Stop-AllServers
        }
        
        "stop" {
            Stop-AllServers
        }
        
        default {
            Write-Host "Usage: entrypoint.ps1 [command]"
            Write-Host "Commands:"
            Write-Host "  all     - Start all server components (default)"
            Write-Host "  connect - Start only connect server"
            Write-Host "  map     - Start only map server"
            Write-Host "  search  - Start only search server"
            Write-Host "  world   - Start only world server"
            Write-Host "  health  - Run health check"
            Write-Host "  stop    - Stop all servers"
            exit 1
        }
    }
} catch {
    Write-Error "Error occurred: $($_.Exception.Message)"
    Stop-AllServers
    exit 1
}

Write-Host "Entrypoint script completed"
exit 0