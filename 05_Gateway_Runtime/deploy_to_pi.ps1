param(
    [string]$PiIP = "192.168.137.2",
    [string]$PiUser = "fyp1512"
)

Write-Host "Deploying upgrades to Autonomous Edge Gateway ($PiIP)" -ForegroundColor Cyan

$scriptDir = $PSScriptRoot
$projectRoot = Split-Path $scriptDir -Parent

$filesToDeploy = @(
    (Join-Path $scriptDir "dashboard.py"),
    (Join-Path $scriptDir "pure_rf_multi.py"),
    (Join-Path $scriptDir "gateway.service"),
    (Join-Path $scriptDir "setup_systemd.sh"),
    (Join-Path $projectRoot "06_Testing_and_Telemetry\plot_stress_test.py"),
    (Join-Path $projectRoot "06_Testing_and_Telemetry\simulate_traffic.py")
)

foreach ($filePath in $filesToDeploy) {
    if (Test-Path $filePath) {
        $fileName = Split-Path $filePath -Leaf
        Write-Host "[*] Pushing $fileName to Pi..." -ForegroundColor Yellow
        scp $filePath "${PiUser}@${PiIP}:~"
    } else {
        Write-Warning "File $filePath not found."
    }
}

Write-Host "`n[SUCCESS] All files transferred to Raspberry Pi." -ForegroundColor Green
