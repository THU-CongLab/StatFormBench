# 🎯 StatFormBench

<p align="center">
  <strong>Benchmarking Language Models for Statistical Problem Formulation</strong>
</p>

  **[English](README.md)** | [中文](README_zh.md)

<p align="center">
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <!-- TODO: Replace XXXX.XXXXX with the actual arXiv ID -->
  <a href="https://arxiv.org/abs/XXXX.XXXXX"><img src="https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg?logo=arxiv&logoColor=white" alt="arXiv paper"></a>
  <a href="https://huggingface.co/datasets/THU-CongLab/StatFormBench"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E" alt="Hugging Face Dataset"></a>
</p>

<p align="center">
  <strong><a href="https://huggingface.co/datasets/THU-CongLab/StatFormBench">Dataset</a></strong> ·
  <strong><a href="https://arxiv.org/abs/XXXX.XXXXX">Paper</a></strong> ·
  <strong><a href="#-usage">Quick Start</a></strong> ·
  <strong><a href="#-license">License</a></strong>
</p>

## 🔍 Dataset Overview

StatFormBench is a benchmark dataset designed to evaluate the ability of Large Language Models (LLMs) in **Statistical Problem Formulation**. This benchmark provides a comprehensive framework for assessing how well LLMs can understand and formulate statistical analysis problems from natural language descriptions.

## 📁 Project Structure

```
statformbench/
├── config/                       # Configuration files
│   ├── api_config.py             # API configuration (key & base_url)
│   └── models.txt                # Model IDs (one per line)
├── data/                         # Dataset and reference data
│   ├── statformbench.json        # Dataset in JSON format
│   ├── statformbench.pkl         # Main dataset file (pickle format, ground truth)
│   └── method_hierarchy.csv      # Method hierarchy mapping for classification
├── prompts/                      # LLM prompt definitions
│   └── prompts.py                # Prompt templates (Prompt_book, Prompt_case)
├── src/                          # Source code
│   ├── run_benchmark.py          # Main execution script
│   └── evaluation/               # Evaluation scripts and modules
│       ├── evaluate_combined.py  # Main evaluation script
│       ├── evaluate_case.py      # Case evaluation module
│       ├── variable_metrics.py   # Variable comparison metrics (Jaccard, PV, RV)
│       ├── compare_methods.py     # Method comparison functions
│       ├── json_utils.py         # JSON extraction utilities
│       ├── llm_evaluate.py       # LLM-based automated evaluation workflow
│       ├── llm_evaluator.py      # LLM model evaluation helper
│       └── role_accuracy.py      # Variable role accuracy module
├── results/                      # Benchmark output storage (model outputs)
├── evaluation_results/           # Evaluation output storage (evaluation scores)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## ⚙️ Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

### 🔑 1. API Configuration

Configure your API credentials in [`config/api_config.py`](config/api_config.py):

```python
api_key = "your_api_key_here"
base_url = "your_base_url_here"
```

### 🤖 2. Model Configuration

Specify the models to evaluate in [`config/models.txt`](config/models.txt). Write **one model ID per line**:

```
gemini-3.1-pro-preview
qwen3.5-397b-a17b
gpt-5.5
claude-opus-4-6
```

Each line corresponds to a model that will be tested against all samples in the dataset.

## 🚀 Usage

### ▶️ Running the Benchmark

Execute the main script to run the benchmark:

```bash
python src/run_benchmark.py
```

The script will:
1. Load samples from `data/statformbench.json`
2. For each sample × model combination, call the LLM API
3. Save results to the `results/` directory (both `.pkl` and `.csv` formats)

### 📊 Running the Evaluation

Evaluation is performed by running the [`src/evaluation/evaluate_combined.py`](src/evaluation/evaluate_combined.py) script, which loads the model outputs (PKL file) and computes the evaluation metrics against the ground truth in `data/statformbench.pkl`.

```bash
python src/evaluation/evaluate_combined.py [optional: pkl_path]
```

- **Script path**: `src/evaluation/evaluate_combined.py`
- **Input**: a PKL file containing model outputs (produced by `src/run_benchmark.py`). If no `pkl_path` argument is provided, the script defaults to `results/all_models_result_other.pkl`.
- **Output**: evaluation results are saved as a CSV file to the `evaluation_results/` directory. The output filename is derived from the input PKL name with an `_evaluated` suffix (e.g., `all_models_result_other_evaluated.csv`).
- **Workflow**: the script reads each sample, looks up the corresponding ground-truth answer from `data/statformbench.pkl`, computes the metrics (JCV, PV, RV, $ACC_{CG}$, $ACC_{FG}$, VRI), and writes the annotated results to CSV.

### 📏 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| JCV | Jaccard Coefficient - measures variable set similarity |
| PV | Precision - proportion of predicted variables that are correct |
| RV | Recall - proportion of correct variables that are predicted |
| $ACC_{CG}$ | Coarse-grained accuracy |
| $ACC_{FG}$ | Fine-grained accuracy |
| VRI | Variable Role Consistency - matching variable roles |

## 📜 License

This project is intended for research purposes. Please refer to the original dataset license for usage restrictions.

## 📝 Citation

If StatFormBench helps your research or work, please consider citing it:

```bibtex
@misc{statformbenchbench, 
  title = {StatFormBench: A Benchmark for Statistical Problem Formulation with LLMs},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/statformbench},
  note = {GitHub repository, accessed 2024}
}
```
