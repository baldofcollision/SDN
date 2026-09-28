#!/usr/bin/env bash
# SOTOPIA 中文版 LaTeX 一键编译脚本
# 用法：./compile.sh
# 需要已安装 TeX Live（含 xelatex）

set -e

echo "========================================"
echo "  SOTOPIA 中文版 LaTeX 一键编译"
echo "========================================"
echo ""

# 检查是否安装 xelatex
if ! command -v xelatex >/dev/null 2>&1; then
    echo "[错误] 未检测到 xelatex！"
    echo "请先安装 TeX Live，并将 xelatex 添加到 PATH。"
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get install texlive-xetex texlive-lang-chinese texlive-latex-extra"
    echo "macOS:"
    echo "  brew install --cask mactex"
    exit 1
fi

echo "[1/3] 第一次编译（生成辅助文件）..."
xelatex -interaction=nonstopmode main.tex || echo "[警告] 第一次编译存在警告或错误，尝试继续..."

echo ""
echo "[2/3] 第二次编译（更新目录与引用）..."
xelatex -interaction=nonstopmode main.tex || echo "[警告] 第二次编译存在警告或错误，尝试继续..."

echo ""
echo "[3/3] 清理中间文件..."
rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot

echo ""
echo "========================================"
echo "  编译完成！"
echo "  输出文件：main.pdf"
echo "========================================"

# 询问是否打开 PDF
if command -v open >/dev/null 2>&1; then
    # macOS
    read -p "是否打开生成的 PDF？(Y/N): " OPENPDF
    if [ "$(echo $OPENPDF | tr 'a-z' 'A-Z')" = "Y" ]; then
        open main.pdf
    fi
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    read -p "是否打开生成的 PDF？(Y/N): " OPENPDF
    if [ "$(echo $OPENPDF | tr 'a-z' 'A-Z')" = "Y" ]; then
        xdg-open main.pdf
    fi
fi
