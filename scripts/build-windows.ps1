$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

if ($null -eq (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path -LiteralPath $vswhere)) {
        throw "Visual Studio Build Tools were not found."
    }
    $installation = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if (-not $installation) {
        throw "Visual Studio C++ Build Tools were not found."
    }
    Import-Module (Join-Path $installation "Common7\Tools\Microsoft.VisualStudio.DevShell.dll")
    Enter-VsDevShell -VsInstallPath $installation -SkipAutomaticLocation -DevCmdArguments "-arch=amd64 -host_arch=amd64"
}

python (Join-Path $repo "scripts\build.py") --platform windows
