# build-and-copy.ps1
# Builds a Docker image from the Dockerfile in the current folder,
# saves it to a tarball, and copies it to a Raspberry Pi user folder.

param(
    [string]$ImageName = "ticketbroker",
    [string]$Tag = "dev",
    [string]$PiHost = "192.168.1.151",
    [string]$PiUser = "magpern",
    [string]$PiPass = "raspberry",
    [string]$PscpPath = "pscp.exe"   # Set full path if not in PATH, e.g. "C:\Program Files\PuTTY\pscp.exe"
)

$ErrorActionPreference = "Stop"

# Basic pre-checks
if (-not (Test-Path -LiteralPath "./Dockerfile")) {
    throw "No Dockerfile found in the current directory."
}

function Test-CommandExists { param([string]$cmd) $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }

if (-not (Test-CommandExists "docker")) {
    throw "Docker CLI not found in PATH."
}

Write-Host "==> Building Docker image ${ImageName}:${Tag} for Linux ARM64 (Raspberry Pi)"
docker build --platform linux/arm64 -t "${ImageName}:${Tag}" .

# Output tar name, e.g. myapp_latest_20251027-134500.tar
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$TarFile = Join-Path (Get-Location) "${ImageName}_${Tag}_$timestamp.tar"

Write-Host "==> Saving image to $TarFile"
docker save "${ImageName}:${Tag}" -o "$TarFile"

# Prefer PSCP (supports -pw). Fallback to OpenSSH scp (prompts for password).
$pscpAvailable = Test-CommandExists -cmd $PscpPath

if ($pscpAvailable) {
    Write-Host "==> Copying with PSCP to ${PiUser}@${PiHost}:/home/${PiUser}/"
    & $PscpPath -pw $PiPass "$TarFile" "${PiUser}@${PiHost}:/home/${PiUser}/"
    if ($LASTEXITCODE -ne 0) {
        throw "PSCP failed with exit code $LASTEXITCODE."
    }
}
else {
    Write-Warning "PSCP not found: $PscpPath"
    if (-not (Test-CommandExists -cmd "scp")) {
        throw "Neither PSCP nor SCP was found. Install PuTTY (pscp.exe) or OpenSSH client."
    }
    Write-Host "==> Copying with OpenSSH scp to ${PiUser}@${PiHost}:/home/${PiUser}/ (you will be prompted for the password)."
    scp "$TarFile" "${PiUser}@${PiHost}:/home/${PiUser}/"
    if ($LASTEXITCODE -ne 0) {
        throw "SCP failed with exit code $LASTEXITCODE."
    }
}

Write-Host "==> Done. File copied to /home/${PiUser}/ on ${PiHost}"
