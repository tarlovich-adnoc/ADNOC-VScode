#Requires -Version 5
$ErrorActionPreference = "Stop"

# Verification gate for the 'dotnet' stack.
# Gates run fail-fast: deps -> format-check -> static-analysis -> test + coverage.
#
# NOTE: $ErrorActionPreference = "Stop" only halts on cmdlet/PowerShell errors, NOT on a
# native executable returning a non-zero exit code. Every gate below is a native command
# (dotnet/npm/npx/fvm/flutter/dart), so we MUST check $LASTEXITCODE after each one or a
# failed gate (e.g. build) would be silently passed over and the script would still print
# success. Invoke-Gate centralizes that check.
function Invoke-Gate([string]$Name, [string[]]$Cmd) {
    Write-Host "==> $Name"
    & $Cmd[0] @($Cmd[1..($Cmd.Count - 1)])
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Name FAILED (exit $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
}

Invoke-Gate "[1/4] dotnet restore" @("dotnet", "restore")

Invoke-Gate "[2/4] format check (dotnet format --verify-no-changes)" @("dotnet", "format", "--verify-no-changes")

Invoke-Gate "[3/4] build (warnings as errors)" @("dotnet", "build", "-warnaserror")

Invoke-Gate "[4/4] test (with coverage)" @("dotnet", "test", "--collect:XPlat Code Coverage")


Write-Host "All verification checks passed."
