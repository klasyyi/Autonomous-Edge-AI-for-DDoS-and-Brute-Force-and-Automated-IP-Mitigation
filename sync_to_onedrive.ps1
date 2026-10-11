$src = $PSScriptRoot
$dst = "C:\Users\syara\OneDrive\Desktop\Final_Year_Final_Sem\FYP_Project"

if ($src.TrimEnd('\') -eq $dst.TrimEnd('\')) {
    Write-Host "[INFO] Already running from master FYP_Project folder: $dst" -ForegroundColor Green
    exit 0
}

Write-Host "Syncing from: $src" -ForegroundColor Cyan
Write-Host "Syncing to  : $dst" -ForegroundColor Cyan

robocopy $src $dst /E /R:1 /W:1 /NP /XD ".git" "__pycache__"

$rc = $LASTEXITCODE
if ($rc -le 7) {
    Write-Host ""
    Write-Host "[SUCCESS] OneDrive FYP_Project is 100% up to date!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Error "[ERROR] Robocopy encountered error code $rc"
}
