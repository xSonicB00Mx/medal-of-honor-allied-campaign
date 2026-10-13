param(
  [string]$CMake,
  [string]$FlexBison,
  [string]$BuildDirectory = 'build-local/cp00',
  [int]$Jobs = 6
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
if (-not $CMake -or -not $FlexBison) { throw 'Pass explicit CMake executable and FlexBison directory.' }
Push-Location $repo
try {
  $env:SOURCE_DATE_EPOCH = (& git show -s --format=%ct HEAD)
  & $CMake -S . -B $BuildDirectory -G 'Visual Studio 17 2022' -A x64 `
    "-DFLEX_EXECUTABLE=$FlexBison/win_flex.exe" "-DBISON_EXECUTABLE=$FlexBison/win_bison.exe" `
    -DUSE_HTTP=OFF -DUSE_RENDERER_DLOPEN=OFF -DBUILD_RENDERER_GL2=OFF
  if ($LASTEXITCODE) { throw 'CMake configure failed' }
  & $CMake --build $BuildDirectory --config RelWithDebInfo --parallel $Jobs
  if ($LASTEXITCODE) { throw 'Engine build failed' }
} finally { Pop-Location }
