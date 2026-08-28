# 🎯 StatFormBench

[English](README.md) | **[中文](README_zh.md)**

<p align="center">
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <!-- TODO: 将 XXXX.XXXXX 替换为实际的 arXiv 编号 -->
  <a href="https://arxiv.org/abs/XXXX.XXXXX"><img src="https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg?logo=arxiv&logoColor=white" alt="arXiv paper"></a>
  <a href="https://huggingface.co/datasets/THU-CongLab/StatFormBench"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E" alt="Hugging Face Dataset"></a>
</p>

<p align="center">
  <strong><a href="https://huggingface.co/datasets/THU-CongLab/StatFormBench">数据集</a></strong> ·
  <strong><a href="https://arxiv.org/abs/XXXX.XXXXX">论文</a></strong> ·
  <strong><a href="#-使用方法">快速开始</a></strong> ·
  <strong><a href="#-评估指标">评估结果</a></strong> ·
  <strong><a href="#-许可证">许可证</a></strong>
</p>

## 🔍 数据集概述

StatFormBench 是一个用于评估大语言模型（LLM）在**统计问题形式化（Statistical Problem Formulation）**能力的基准数据集。该基准提供了一个综合框架，用于评估 LLM 从自然语言描述中理解和形式化统计分析问题的能力。


## 📁 项目结构

```
statformbench/
├── config/                       # 配置文件
│   ├── api_config.py             # API 配置（密钥与 base_url）
│   └── models.txt                # 模型 ID（每行一个）
├── data/                         # 数据集与参考数据
│   ├── statformbench.json        # JSON 格式数据集
│   ├── statformbench.pkl         # 主数据集文件（pickle 格式，标准答案）
│   └── method_hierarchy.csv      # 方法层级映射（用于分类任务）
├── prompts/                      # LLM 提示词定义
│   └── prompts.py                # 提示词模板（Prompt_book、Prompt_case）
├── src/                          # 源代码
│   ├── run_benchmark.py          # 主执行脚本
│   └── evaluation/               # 评估脚本和模块
│       ├── evaluate_combined.py  # 主评估脚本
│       ├── evaluate_case.py      # Case 评估模块
│       ├── variable_metrics.py   # 变量比较指标（Jaccard、PV、RV）
│       ├── compare_methods.py     # 方法比较函数
│       ├── json_utils.py         # JSON 提取工具
│       ├── llm_evaluate.py       # 基于 LLM 的自动化评估流程
│       ├── llm_evaluator.py      # LLM 模型评估辅助
│       └── role_accuracy.py      # 变量角色准确率模块
├── results/                      # 基准测试输出存储（模型输出）
├── evaluation_results/           # 评估输出存储（评估得分）
├── requirements.txt              # Python 依赖
└── README.md                     # 本文件
```

## ⚙️ 安装

安装所需的 Python 依赖：

```bash
pip install -r requirements.txt
```


## 🔧 配置

### 🔑 1. API 配置

在 [`config/api_config.py`](config/api_config.py) 中配置你的 API 凭证：

```python
api_key = "你的_api_key"
base_url = "你的_base_url"
```

### 🤖 2. 模型配置

在 [`config/models.txt`](config/models.txt) 中指定需要评估的模型。**每行写一个模型 ID**：

```
gemini-3.1-pro-preview
qwen3.5-397b-a17b
gpt-5.5
claude-opus-4-6
```

每一行对应一个模型，该模型将与数据集中的所有样本进行测试。

## 🚀 使用方法

### ▶️ 运行测试

执行主脚本运行基准测试：

```bash
python src/run_benchmark.py
```

脚本将执行以下操作：
1. 从 `data/statformbench.json` 加载样本
2. 对每个「样本 × 模型」组合调用 LLM API
3. 将结果保存到 `results/` 目录（同时输出 `.pkl` 和 `.csv` 格式）

### 📊 运行评估

评测需要运行 [`src/evaluation/evaluate_combined.py`](src/evaluation/evaluate_combined.py) 脚本。该脚本会加载模型输出（PKL 文件），并与 `data/statformbench.pkl` 中的标准答案进行比对，计算评估指标。

```bash
python src/evaluation/evaluate_combined.py [可选: pkl_path]
```

- **脚本路径**：`src/evaluation/evaluate_combined.py`
- **输入**：包含模型输出的 PKL 文件（由 `src/run_benchmark.py` 生成）。若未提供 `pkl_path` 参数，脚本默认使用 `results/all_models_result_other.pkl`。
- **输出**：评估结果以 CSV 文件形式保存到 `evaluation_results/` 目录。输出文件名由输入 PKL 文件名加 `_evaluated` 后缀生成（如 `all_models_result_other_evaluated.csv`）。
- **流程**：脚本逐条读取样本，从 `data/statformbench.pkl` 中查找对应的标准答案，计算各项指标（JCV、PV、RV、$ACC_{CG}$、$ACC_{FG}$、VRI），并将带有评估指标的结果写入 CSV 文件。

### 📏 评估指标

| 指标 | 说明 |
|------|------|
| JCV | Jaccard 系数 - 衡量变量集合的相似度 |
| PV | 精确率 - 预测变量中正确的比例 |
| RV | 召回率 - 正确变量中被预测到的比例 |
| $ACC_{CG}$ | 粗粒度准确率 |
| $ACC_{FG}$ | 细粒度准确率 |
| VRI | 变量角色一致性 - 匹配变量角色 |


## 📜 许可证

本项目仅供研究使用。使用限制请参阅原始数据集许可证。

## 📝 引用

如果 StatFormBench 对您的研究或工作有所帮助，欢迎引用：

```bibtex
@misc{statformbenchbench, 
  title = {StatFormBench: A Benchmark for Statistical Problem Formulation with LLMs},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/statformbench},
  note = {GitHub repository, accessed 2024}
}
```
