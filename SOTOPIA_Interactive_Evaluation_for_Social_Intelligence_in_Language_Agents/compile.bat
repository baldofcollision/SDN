@echo off
:: SOTOPIA 中文版 LaTeX 一键编译脚本
:: 用法：双击运行，或在 PowerShell/CMD 中执行
:: 需要已安装 TeX Live 或 MiKTeX，并将 xelatex 添加到 PATH

echo ========================================
echo   SOTOPIA 中文版 LaTeX 一键编译
echo ========================================
echo.

:: 检查是否安装 xelatex
where xelatex >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 xelatex！
    echo 请先安装 TeX Live 或 MiKTeX，并将 xelatex 添加到 PATH。
    echo 下载地址：
    echo   - TeX Live: https://tug.org/texlive/
    echo   - MiKTeX:  https://miktex.org/
    pause
    exit /b 1
)

echo [1/3] 第一次编译（生成辅助文件）...
xelatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo [警告] 第一次编译存在警告或错误，尝试继续...
)

echo.
echo [2/3] 第二次编译（更新目录与引用）...
xelatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo [警告] 第二次编译存在警告或错误，尝试继续...
)

echo.
echo [3/3] 清理中间文件（可选）...
del /Q *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot 2>nul >nul

echo.
echo ========================================
echo   编译完成！
echo   输出文件：main.pdf
echo ========================================
echo.

:: 询问是否打开 PDF
set /p OPENPDF="是否打开生成的 PDF？(Y/N): "
if /I "%OPENPDF%"=="Y" (
    start main.pdf
)

pause
