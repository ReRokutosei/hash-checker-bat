param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("-i", "-s")]
    [string]$Mode,
    
    [Parameter(Position=1, Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$Files
)

function Get-FileHash($filePath) {
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    
    try {
        $stream = [System.IO.File]::OpenRead($filePath)
        return @{
            'MD5' = [System.BitConverter]::ToString($md5.ComputeHash($stream)).Replace("-", "").ToLower()
            'SHA1' = [System.BitConverter]::ToString($sha1.ComputeHash($stream)).Replace("-", "").ToLower()
            'SHA256' = [System.BitConverter]::ToString($sha256.ComputeHash($stream)).Replace("-", "").ToLower()
        }
    }
    finally {
        if ($stream) { $stream.Dispose() }
        $md5.Dispose()
        $sha1.Dispose()
        $sha256.Dispose()
    }
}

function Print-Hashes($file, $hashes) {
    Write-Host "`n文件: $([System.IO.Path]::GetFileName($file))"
    Write-Host "--------------------------------------"
    $hashes.GetEnumerator() | ForEach-Object {
        Write-Host "$($_.Key):    $($_.Value)"
    }
    Write-Host "--------------------------------------"
}

function Info-Mode($files) {
    $found = $false
    foreach ($pattern in $files) {
        $matches = Resolve-Path $pattern -ErrorAction SilentlyContinue
        if (-not $matches) { continue }
        
        foreach ($file in $matches) {
            if (Test-Path $file.Path -PathType Leaf) {
                $found = $true
                try {
                    $hashes = Get-FileHash $file.Path
                    Print-Hashes $file.Path $hashes
                }
                catch {
                    Write-Host "处理文件 $file 时出错：$_"
                }
            }
        }
    }
    
    if (-not $found) {
        Write-Host "未找到匹配的文件"
    }
}

function Compare-Mode($files) {
    $allFiles = @()
    foreach ($pattern in $files) {
        $matches = Resolve-Path $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $allFiles += $matches | Where-Object { Test-Path $_.Path -PathType Leaf }
        }
    }
    
    if ($allFiles.Count -lt 2) {
        Write-Host "错误：比较模式需要至少两个文件"
        return
    }
    
    $firstFile = $allFiles[0].Path
    $firstHashes = Get-FileHash $firstFile
    Print-Hashes $firstFile $firstHashes
    
    $allSame = $true
    $diffFiles = @()
    
    foreach ($file in $allFiles[1..($allFiles.Count-1)]) {
        $currentHashes = Get-FileHash $file.Path
        Print-Hashes $file.Path $currentHashes
        
        $isDifferent = $false
        foreach ($key in $firstHashes.Keys) {
            if ($firstHashes[$key] -ne $currentHashes[$key]) {
                $isDifferent = $true
                break
            }
        }
        
        if ($isDifferent) {
            $allSame = $false
            $diffFiles += [System.IO.Path]::GetFileName($file.Path)
        }
    }
    
    Write-Host ""
    if ($allSame) {
        Write-Host "******✅ 所有文件哈希值相同******"
    }
    else {
        Write-Host "******⚠️ 存在不一致的哈希值******"
        Write-Host "以下文件与`"$([System.IO.Path]::GetFileName($firstFile))`"的哈希值不同：$($diffFiles -join ' ')"
    }
}

try {
    switch ($Mode) {
        "-i" { Info-Mode $Files }
        "-s" { Compare-Mode $Files }
    }
}
catch {
    Write-Host "执行过程中出错：$_"
}
