# SOTOPIA 中文翻译版编译说明

## 文件清单

- `main.tex`：LaTeX 源文件（已完整翻译为中文）
- `SOTOPIA_Interactive_Evaluation_for_Social_Intelligence_in_Language_Agents.pdf`：英文原版 PDF
- `promt_translation.md`：翻译要求文档
- `paper_full.txt`：从英文 PDF 提取的纯文本（中间产物）
- `extract_pdf.py`：PDF 文本提取脚本（中间产物）

## 编译方法

### 方法一：使用本地 TeX Live / MiKTeX

#### Linux / macOS：

```bash
xelatex main.tex
xelatex main.tex   # 第二次以生成完整目录、引用与图表编号
```

#### Windows（PowerShell）：

```powershell
xelatex main.tex
xelatex main.tex
```

如果使用 MiKTeX，第一次编译时可能会自动下载缺失的宏包。

### 方法二：使用在线 LaTeX 编辑器

1. 访问 [Overleaf](https://www.overleaf.com)（推荐）
2. 新建项目 → 上传 `main.tex`
3. 编译器选择 **XeLaTeX**
4. 点击 "Recompile"

### 方法三：使用 Docker

```bash
docker run --rm -v $(pwd):/workdir -w /workdir texlive/texlive:latest xelatex main.tex
```

## 必需宏包

文档使用以下宏包，请确保您的 TeX 发行版包含这些宏包：

- `ctex` 或 `xeCJK`（中文支持）
- `amsmath`, `amssymb`, `amsfonts`（数学符号）
- `graphicx`（图形）
- `booktabs`, `tabularx`, `multirow`, `multicol`（表格）
- `array`, `longtable`
- `hyperref`（超链接）
- `geometry`（页面布局）
- `xcolor`（颜色）
- `listings`（代码片段）
- `titlesec`（标题格式）
- `fancyhdr`（页眉页脚）

## 系统要求

### Windows

安装 [TeX Live](https://tug.org/texlive/) 或 [MiKTeX](https://miktex.org/)。

### macOS

推荐安装 MacTeX：
```bash
brew install --cask mactex
```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-lang-chinese texlive-latex-extra

# Fedora
sudo dnf install texlive-xetex texlive-collection-langchinese
```

## 可能遇到的问题及解决方案

### 1. 中文字体问题

如果出现中文字体警告，请确保系统安装了中文字体（如 SimSun、SimHei 或 Noto Sans CJK SC）。ctex 宏包会自动选择系统中可用的中文字体。

### 2. 宏包缺失

- **MiKTeX**：会自动下载缺失的宏包
- **TeX Live**：使用 `tlmgr install <package>` 安装缺失的宏包

### 3. 编码问题

文档使用 UTF-8 编码。如果遇到编码问题，请确保编辑器以 UTF-8 打开文件。

### 4. 图片缺失

由于本翻译版未包含原 PDF 中的所有图片（部分为示意图），编译器可能会跳过来自外部 `.pdf/.png/.jpg` 的图片。如需添加图片，请将原始图片放置于与 `main.tex` 相同的目录中，并使用 `\includegraphics{figure.pdf}` 命令引用。

## 翻译说明

- 本翻译严格遵循 `promt_translation.md` 中规定的学术规范与术语标准
- 采用规范的中文学术论文语体，句意准确严谨
- 中英对照术语在首次出现时给出，例如：
  - 注意力机制（Attention Mechanism）
  - 分布外（Out-of-Distribution, OOD）
  - 键值缓存（Key-Value Cache, KV Cache）
- 经典模型名（Transformer、BERT、GPT-4 等）、数据集（ImageNet、MMLU、GSM8K 等）、软件名（PyTorch、CUDA 等）保留英文不译

## 联系

如有任何问题，请参考原论文获取更多信息：
- 项目主页：https://sotopia.world
- 原论文：ICLR 2024
