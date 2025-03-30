@echo off
setlocal enabledelayedexpansion

:: 检查参数
if "%~1"=="" (
    echo 用法：
    echo hash -i file           计算单个或多个文件的哈希值
    echo hash -s file1 file2    比较两个或多个文件的哈希值
    exit /b 1
)

:: 检查操作模式
if "%~1"=="-i" (
    if "%~2"=="" (
        echo 错误：请指定要计算哈希值的文件
        exit /b 1
    )
    goto :info_mode
) else if "%~1"=="-s" (
    if "%~2"=="" (
        echo 错误：比较模式需要至少两个文件
        exit /b 1
    )
    goto :compare_mode
) else (
    echo 错误：无效的操作模式，请使用 -i 或 -s
    exit /b 1
)

:info_mode
shift
set "found=0"
:info_loop
if "%~1"=="" (
    if !found!==0 echo 未找到匹配的文件
    goto :eof
)

setlocal disabledelayedexpansion
pushd "%~dp1" 2>nul && (
    if exist "%~nx1" (
        endlocal
        setlocal enabledelayedexpansion
        set "found=1"
        echo.
        echo 文件: %~nx1
        echo --------------------------------------
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~nx1" MD5 ^| findstr /v "CertUtil"`) do echo MD5:    %%a
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~nx1" SHA1 ^| findstr /v "CertUtil"`) do echo SHA1:   %%a
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~nx1" SHA256 ^| findstr /v "CertUtil"`) do echo SHA256: %%a
        echo --------------------------------------
    ) else (
        endlocal
        setlocal enabledelayedexpansion
    )
    popd
) || (
    if exist "%~f1" (
        endlocal
        setlocal enabledelayedexpansion
        set "found=1"
        echo.
        echo 文件: %~nx1
        echo --------------------------------------
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~f1" MD5 ^| findstr /v "CertUtil"`) do echo MD5:    %%a
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~f1" SHA1 ^| findstr /v "CertUtil"`) do echo SHA1:   %%a
        for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "%~f1" SHA256 ^| findstr /v "CertUtil"`) do echo SHA256: %%a
        echo --------------------------------------
    ) else (
        endlocal
        setlocal enabledelayedexpansion
    )
)
shift
goto :info_loop

:compare_mode
set "found=0"
set "file_count=0"
set "params_count=0"

:: 预处理所有参数，包括通配符展开
setlocal disabledelayedexpansion
for %%x in (%*) do (
    if not "%%~x"=="-s" (
        endlocal
        setlocal enabledelayedexpansion
        set /a "params_count+=1"
        setlocal disabledelayedexpansion
        pushd "%%~dpx" 2>nul && (
            if exist "%%~nxx" (
                endlocal
                setlocal enabledelayedexpansion
                set "param_!params_count!=%%~fx"
                set /a "valid_files+=1"
            ) else (
                endlocal
                setlocal enabledelayedexpansion
            )
            popd
        ) || (
            if exist "%%~fx" (
                endlocal
                setlocal enabledelayedexpansion
                set "param_!params_count!=%%~fx"
                set /a "valid_files+=1"
            ) else (
                endlocal
                setlocal enabledelayedexpansion
            )
        )
    )
)

:: 检查实际存在的文件数量
if !valid_files! lss 2 (
    echo 错误：比较模式需要至少两个文件
    exit /b 1
)

:: 获取第一个有效文件
for /L %%i in (1,1,!params_count!) do (
    if exist "!param_%%i!" (
        set "first_file=!param_%%i!"
        set "found=1"
        goto :process_first_file
    )
)

:process_first_file
:: 保存第一个文件的哈希值
for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!first_file!" MD5 ^| findstr /v "CertUtil"`) do set "md5_1=%%a"
for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!first_file!" SHA1 ^| findstr /v "CertUtil"`) do set "sha1_1=%%a"
for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!first_file!" SHA256 ^| findstr /v "CertUtil"`) do set "sha256_1=%%a"

echo.
echo 文件: !first_file!
echo --------------------------------------
echo MD5:    !md5_1!
echo SHA1:   !sha1_1!
echo SHA256: !sha256_1!
echo --------------------------------------

set "all_same=1"
set "diff_files="
set "processed_first=0"

:: 处理所有其他文件
for /L %%i in (1,1,!params_count!) do (
    if exist "!param_%%i!" (
        if not "!param_%%i!"=="!first_file!" (
            echo.
            echo 文件: !param_%%i!
            echo --------------------------------------
            for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!param_%%i!" MD5 ^| findstr /v "CertUtil"`) do (
                set "md5_2=%%a"
                echo MD5:    %%a
            )
            for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!param_%%i!" SHA1 ^| findstr /v "CertUtil"`) do (
                set "sha1_2=%%a"
                echo SHA1:   %%a
            )
            for /f "skip=1 tokens=* usebackq" %%a in (`certutil -hashfile "!param_%%i!" SHA256 ^| findstr /v "CertUtil"`) do (
                set "sha256_2=%%a"
                echo SHA256: %%a
            )
            echo --------------------------------------

            if not "!md5_1!"=="!md5_2!" (
                set "all_same=0"
                set "diff_files=!diff_files! !param_%%i!"
            ) else if not "!sha1_1!"=="!sha1_2!" (
                set "all_same=0"
                set "diff_files=!diff_files! !param_%%i!"
            ) else if not "!sha256_1!"=="!sha256_2!" (
                set "all_same=0"
                set "diff_files=!diff_files! !param_%%i!"
            )
        )
    )
)

:: 显示结果
echo.
if !all_same!==1 (
    echo ******✅ 所有文件哈希值相同******
) else (
    echo ******⚠️ 存在不一致的哈希值******
    echo 以下文件与"!first_file!"的哈希值不同：!diff_files!
)
goto :eof
