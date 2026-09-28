# 本地编译指南

## 编译方式

使用 XeLaTeX 编译（推荐）：

```bash
xelatex RoCo_Translation.tex
```

或使用完整编译链（解决交叉引用）：

```bash
xelatex RoCo_Translation.tex
bibtex RoCo_Translation.aux
xelatex RoCo_Translation.tex
xelatex RoCo_Translation.tex
```

## 依赖环境

- TeX Live 2020+ 或 MiKTeX
- XeLaTeX 引擎
- 中文字体（如 Noto Serif CJK, Source Han Serif CN 等）

## 字体配置

如需使用系统自带中文字体，请确保安装了支持中文的字体包。ctex 宏包会自动处理字体配置。

## 常见问题

1. **字体缺失**：安装 `fonts-noto-cjk` 或使用其他中文字体
2. **编译超时**：增加 TeX Live 缓存大小
3. **图片路径**：所有图片文件需放在 `./images/` 目录下
