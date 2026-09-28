# AgentBench 中文翻译版编译说明

## 编译步骤

本工程已通过 **XeLaTeX** 编译验证（TeX Live 2026）。编译步骤如下：

```powershell
cd d:\Agent_evaluaion\SDN\AgentBench_Evaluating_LLMs_as_Agents\translation
xelatex -interaction=nonstopmode main.tex   # 第 1 遍
xelatex -interaction=nonstopmode main.tex   # 第 2 遍：解决交叉引用
# (可选) 第 3 遍以保证目录/引用完全稳定
```

## 工程结构

```
translation/
├── main.tex              # 主入口（含 preamble、章节组装）
├── sections/             # 各章节翻译源文件
│   ├── abstract.tex      # 摘要
│   ├── intro.tex         # 第 1 节：引言
│   ├── definition.tex    # 第 2 节：定义与预备
│   ├── composition.tex   # 第 3 节：基准构成
│   ├── evaluation.tex    # 第 4 节：评测
│   ├── related.tex       # 第 5 节：相关工作
│   ├── conclusion.tex    # 第 6 节：结论
│   ├── ack.tex           # 致谢
│   ├── references.tex    # 参考文献
│   ├── appA.tex          # 附录 A：评估框架
│   ├── appB.tex          # 附录 B：操作系统
│   ├── appC.tex          # 附录 C：数据库
│   ├── appD.tex          # 附录 D：知识图谱
│   ├── appE.tex          # 附录 E：数字卡牌游戏
│   ├── appF.tex          # 附录 F：横向思维谜题
│   ├── appG.tex          # 附录 G：家务整理
│   ├── appH.tex          # 附录 H：网页购物
│   ├── appI.tex          # 附录 I：网页浏览
│   └── appJ.tex          # 附录 J：详细分析
├── figures/              # 占位图（可替换为正式中文图）
│   ├── overview_placeholder.png     # 图 1
│   ├── realworld_placeholder.png    # 图 2
│   ├── table1_placeholder.png       # 表 1
│   ├── framework_placeholder.png    # 图 5
│   └── validity_placeholder.png     # 图 6
└── main.pdf              # 编译产物（中译 PDF，44 页）
```

## 依赖与跨平台说明

### 工具
- **XeLaTeX**（TeX Live 2019+）
- **ctex** 中文宏包（自动选用系统中文字体）

### 必要宏包
`ctex` · `xeCJK` · `fontspec` · `natbib` · `amsthm` · `amsmath` · `graphicx`
`booktabs` · `tabularx` · `multirow` · `enumitem` · `titlesec` · `caption`
`hyperref` · `xcolor` · `geometry` · `algorithm` · `algorithmic`

### 中文字体（Windows 下默认）
- 宋体（SimSun）· 黑体（SimHei）· 仿宋（FangSong）· 楷体（KaiTi）

如在 Linux 或 macOS 下编译，请将 `main.tex` 中的字体名替换为：
- Linux：`Noto Serif CJK SC` / `Source Han Serif SC` 等
- macOS：`Songti SC` / `STSong` 等

## 术语与命名规范

严格遵循 `promt_translation.md` 的术语表与专有名词保留法则：

| 英文 | 规范译名 |
|---|---|
| LLM | 大语言模型 |
| Chain-of-Thought (CoT) | 思维链 |
| Ground Truth | 真实值 / 标注真值 |
| Fine-tuning | 微调 |
| Hallucination | 幻觉 |
| Overfitting / Underfitting | 过拟合 / 欠拟合 |
| KV Cache | 键值缓存 |
| Zero-shot / Few-shot | 零样本 / 少样本 |
| Prompt | 提示词 |
| Mixture of Experts | 专家混合架构（MoE） |

模型专名（Transformer / GPT-4 / LLaMA / BERT / RoPE / LoRA / AdamW / FlashAttention）、
数据集（MMLU / GSM8K / SQuAD / BLEU-4 等）、硬件平台（CUDA / PyTorch / H100）
均保留英文。

## 占位图说明

`figures/*.png` 是占位图，用于在缺少原图嵌入的情况下维持编译流畅。
请在替换正式中文图表后重新编译：

| 占位文件 | 对应原图 | 内容 |
|---|---|---|
| `overview_placeholder.png`  | 图 1 | LLM 总体表现柱状图 |
| `realworld_placeholder.png` | 图 2 | 8 类真实环境示意 |
| `table1_placeholder.png`    | 表 1 | 29 个 LLM 模型表 |
| `framework_placeholder.png` | 图 5 | AgentBench 工具包结构 |
| `validity_placeholder.png`  | 图 6 | 模型有效性分析饼图 |

## 成果 PDF

编译后的 PDF 已复制到工作目录根下：

```
d:\Agent_evaluaion\SDN\AgentBench_Evaluating_LLMs_as_Agents\
    AgentBench_Chinese_Translation.pdf    (~550 KB, 44 页)
```

内容覆盖：
- 中文摘要
- 第 1–6 节主体内容（引言 / 定义与预备 / 基准构成 / 评测 / 相关工作 / 结论）
- 致谢
- 完整参考文献（保留英文原版，便于国际追溯）
- 附录 A–J 共 10 个附录（含评估框架 + 8 个环境的详细说明 + 详细分析）
