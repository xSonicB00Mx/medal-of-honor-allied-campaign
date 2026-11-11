# Embedded as a single PowerShell command in Update-Allied-Campaign.cmd.
# No execution-policy changes, elevation, wildcard deletions or profile writes.
$ErrorActionPreference = 'Stop';
function Get-AcHash([string]$path) {
    $stream = [IO.File]::OpenRead($path);
    $sha = [Security.Cryptography.SHA256]::Create();
    try { return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant(); }
    finally { $stream.Dispose(); $sha.Dispose(); };
};
try {
    $root = [IO.Path]::GetFullPath($env:AC_RELEASE_ROOT).TrimEnd('\');
    $manifest = Get-Content -LiteralPath (Join-Path $root 'Allied-Campaign-manifest.json') -Raw | ConvertFrom-Json;
    if ($manifest.version -ne '1.0.1' -or $manifest.obsolete_packages.Count -ne 68) { throw 'Invalid Allied Campaign 1.0.1 manifest.' };
    foreach ($folder in @('main','mainta','maintt')) {
        $dir = Get-Item -LiteralPath (Join-Path $root $folder);
        if ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked game folders are not supported by this updater.' };
        if (-not (Test-Path -LiteralPath (Join-Path $dir.FullName 'zz_AlliedCampaign.pk3') -PathType Leaf)) { throw 'Extract the complete 1.0.1 ZIP first. A consolidated package is missing.' };
    };
    $pending = @();
    foreach ($entry in $manifest.obsolete_packages) {
        if ($entry.path -notmatch '^(main|mainta|maintt)/z+_AC_[A-Za-z0-9_-]+\.pk3$') { throw 'Invalid legacy package path.' };
        $path = [IO.Path]::GetFullPath((Join-Path $root $entry.path));
        if (-not $path.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Legacy path escapes the installation.' };
        if (Test-Path -LiteralPath $path) {
            $item = Get-Item -LiteralPath $path;
            if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Invalid legacy package type.' };
            if ((Get-AcHash $path) -ne $entry.sha256) { throw ('Modified legacy package: ' + $entry.path + '. Nothing was removed. Move it out of the game folders manually after making a backup.'); };
            $pending += $path;
        };
    };
    foreach ($folder in @('main','mainta','maintt')) {
        foreach ($item in Get-ChildItem -LiteralPath (Join-Path $root $folder) -File -Filter '*_AC_*.pk3') {
            if ($pending -notcontains $item.FullName) { throw ('Unrecognized old AC package: ' + $item.Name + '. Nothing was removed.'); };
        };
    };
    if ($pending.Count -gt 0) {
        if (Get-Process -Name openmohaa,mohaa,moh_spearhead,moh_breakthrough -ErrorAction SilentlyContinue) { throw 'Close the game before updating Allied Campaign.' };
        foreach ($folder in @('main','mainta','maintt')) {
            $relative = $folder + '/zz_AlliedCampaign.pk3';
            $expected = @($manifest.files | Where-Object { $_.path -eq $relative });
            if ($expected.Count -ne 1 -or (Get-AcHash (Join-Path $root $relative)) -ne $expected[0].sha256) { throw 'Consolidated package checksum failed. Extract the complete ZIP again. Nothing was removed.' };
        };
        foreach ($path in $pending) { Remove-Item -LiteralPath $path -Force -ErrorAction Stop; };
        Write-Host ('Allied Campaign updated: removed ' + $pending.Count + ' legacy packages. The 3 consolidated packages are ready. Saves and settings were preserved.');
    };
    exit 0;
} catch {
    Write-Host ('Allied Campaign update stopped: ' + $_.Exception.Message);
    exit 1;
};
