@echo off
chcp 65001 >nul
REM Obsidian Context 一键同步脚本

echo ========================================
echo   Obsidian -^> GitHub 同步
echo ========================================
echo.

set "SCRIPT_PATH=D:\Coding\context-sync-system\obsidian-sync.py"

if "%~1"=="--watch" (
    echo [模式] 自动监控模式
    echo [提示] 按 Ctrl+C 停止
    echo.
    python "%SCRIPT_PATH%" --daemon
) else if "%~1"=="--once" (
    echo [模式] 手动同步一次
    echo.
    python "%SCRIPT_PATH%" --once
) else (
    echo 使用方法:
    echo   obsidian-sync.bat --once    手动同步一次
    echo   obsidian-sync.bat --watch   启动自动监控
    echo.
    echo 默认执行手动同步...
    echo.
    python "%SCRIPT_PATH%" --once
)

echo.
pause
