# statformbench

[English](README.md) | **[中文](README_zh.md)**

## 数据集概述

statformbench 是一个用于评估大语言模型（LLM）在**统计问题形式化（Statistical Problem Formulation）**能力的基准数据集。该基准提供了一个综合框架，用于评估 LLM 从自然语言描述中理解和形式化统计分析问题的能力。


## 项目结构

```
statformbench/
├── evaluation/          # 评估脚本和模块
│   ├── evaluate_combined.py   # 主评估脚本
│   ├── test_0.py              # Case 评估模块
│   ├── var.py                 # 变量比较工具
│   ├── compare_methods.py     # 方法比较函数
│   ├── extract_last_json_safe.py  # JSON 提取工具
│   ├── auto_evaluate.py       # 自动化评估流程
│   ├── auto_m0.py             # 模型评估辅助
│   └── role.py                # 角色分析模块
├── results/             # 结果存储目录
├── statformbench.pkl     # 主数据集文件（pickle 格式）
├── statformbench.json    # JSON 格式数据集
├── api_info.py           # API 配置（密钥与 base_url）
├── model_name0.txt       # 模型 ID（每行一个）
├── run.py                # 主执行脚本
├── sta.csv               # 分类任务的补充数据
└── README.md             # 本文件
```

## 安装

安装所需的 Python 依赖：

```bash
pip install -r requirements.txt
```


## 配置

### 1. API 配置

在 [`api_info.py`](api_info.py) 中配置你的 API 凭证：

```python
api_key = "你的_api_key"
base_url = "你的_base_url"
```

### 2. 模型配置

在 [`model_name0.txt`](model_name0.txt) 中指定需要评估的模型。**每行写一个模型 ID**：

```
gemini-3.1-pro-preview
qwen3.5-397b-a17b
gpt-5.5
claude-opus-4-6
```

每一行对应一个模型，该模型将与数据集中的所有样本进行测试。

## 使用方法

### 运行测试

执行主脚本运行基准测试：

```bash
python run.py
```

脚本将执行以下操作：
1. 从 `statformbench.json` 加载样本
2. 对每个「样本 × 模型」组合调用 LLM API
3. 将结果保存到 `results/` 目录（同时输出 `.pkl` 和 `.csv` 格式）

### 运行评估

评测需要运行 [`evaluation/evaluate_combined.py`](evaluation/evaluate_combined.py) 脚本。该脚本会加载模型输出（PKL 文件），并与 `statformbench.pkl` 中的标准答案进行比对，计算评估指标。

```bash
python evaluation/evaluate_combined.py [可选: pkl_path]
```

- **脚本路径**：`evaluation/evaluate_combined.py`
- **输入**：包含模型输出的 PKL 文件（由 `run.py` 生成）。若未提供 `pkl_path` 参数，脚本默认使用 `results/all_models_result_other.pkl`。
- **输出**：评估结果以 CSV 文件形式保存到 `evaluation/evaluation_results/` 目录。输出文件名由输入 PKL 文件名加 `_evaluated` 后缀生成（如 `all_models_result_other_evaluated.csv`）。
- **流程**：脚本逐条读取样本，从 `statformbench.pkl` 中查找对应的标准答案，计算各项指标（JCV、PV、RV、ACC@1st、ACC@2nd、VRI），并将带有评估指标的结果写入 CSV 文件。

### 评估指标

| 指标 | 说明 |
|------|------|
| JCV | Jaccard 系数 - 衡量变量集合的相似度 |
| PV | 精确率 - 预测变量中正确的比例 |
| RV | 召回率 - 正确变量中被预测到的比例 |
| $ACC_{CG}$ | 方法准确率（宽松匹配） |
| $ACC_{FG}$ | 方法准确率（严格精确匹配） |
| VRI | 变量角色一致性 - 匹配变量角色 |


## 许可证

本项目仅供研究使用。使用限制请参阅原始数据集许可证。

## 引用

如果 statformbench 对您的研究或工作有所帮助，欢迎引用：

```bibtex
@misc{statformbench,
  title = {statformbench: A Benchmark for Statistical Problem Formulation with LLMs},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/statformbench},
  note = {GitHub repository, accessed 2024}
}
```
