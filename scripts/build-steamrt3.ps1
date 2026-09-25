$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $repo "build-dependencies.json") -Raw | ConvertFrom-Json

if ($null -ne (Get-Command docker.exe -ErrorAction SilentlyContinue)) {
    $mount = $repo.Replace("\", "/")
    docker run --rm `
        --volume "${mount}:/work" `
        --workdir /work `
        $manifest.steamrt3_image `
        bash /work/scripts/build-linux.sh --install-tools
    exit $LASTEXITCODE
}

if ($null -eq (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw "Docker or WSL with Docker is required for the SteamRT3 build."
}
$mount = (& wsl.exe -d Ubuntu -- wslpath -a $repo.Replace("\", "/")).Trim()
& wsl.exe -d Ubuntu -- docker run --rm `
    --volume "${mount}:/work" `
    --workdir /work `
    $manifest.steamrt3_image `
    bash /work/scripts/build-linux.sh --install-tools
if ($LASTEXITCODE -ne 0) {
    throw "SteamRT3 build failed with exit code $LASTEXITCODE."
}
