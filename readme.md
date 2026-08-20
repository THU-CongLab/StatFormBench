# 🎯 StatFormBench

**[English](README.md)** | [中文](README_zh.md)

## 🔍 Dataset Overview

StatFormBench is a benchmark dataset designed to evaluate the ability of Large Language Models (LLMs) in **Statistical Problem Formulation**. This benchmark provides a comprehensive framework for assessing how well LLMs can understand and formulate statistical analysis problems from natural language descriptions.

## 📁 Project Structure

```
statformbench/
├── evaluation/          # Evaluation scripts and modules
│   ├── evaluate_combined.py   # Main evaluation script
│   ├── test_0.py              # Case evaluation module
│   ├── var.py                 # Variable comparison utilities
│   ├── compare_methods.py     # Method comparison functions
│   ├── extract_last_json_safe.py  # JSON extraction utilities
│   ├── auto_evaluate.py       # Automated evaluation workflow
│   ├── auto_m0.py             # Model evaluation helper
│   └── role.py                # Role analysis module
├── results/             # Results storage
├── statformbench.pkl     # Main dataset file (pickle format)
├── statformbench.json    # Dataset in JSON format
├── api_info.py           # API configuration (key & base_url)
├── model_name0.txt       # Model IDs (one per line)
├── run.py                # Main execution script
├── sta.csv               # Supplementary data for Classification
└── README.md             # This file
```

## ⚙️ Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

### 🔑 1. API Configuration

Configure your API credentials in [`api_info.py`](api_info.py):

```python
api_key = "your_api_key_here"
base_url = "your_base_url_here"
```

### 🤖 2. Model Configuration

Specify the models to evaluate in [`model_name0.txt`](model_name0.txt). Write **one model ID per line**:

```
gemini-3.1-pro-preview
qwen3.5-397b-a17b
gpt-5.5
claude-opus-4-6
```

Each line corresponds to a model that will be tested against all samples in the dataset.

## 🚀 Usage

### ▶️ Running the Test

Execute the main script to run the benchmark:

```bash
python run.py
```

The script will:
1. Load samples from `statformbench.json`
2. For each sample × model combination, call the LLM API
3. Save results to the `results/` directory (both `.pkl` and `.csv` formats)

### 📊 Running the Evaluation

Evaluation is performed by running the [`evaluation/evaluate_combined.py`](evaluation/evaluate_combined.py) script, which loads the model outputs (PKL file) and computes the evaluation metrics against the ground truth in `statformbench.pkl`.

```bash
python evaluation/evaluate_combined.py [optional: pkl_path]
```

- **Script path**: `evaluation/evaluate_combined.py`
- **Input**: a PKL file containing model outputs (produced by `run.py`). If no `pkl_path` argument is provided, the script defaults to `results/all_models_result_other.pkl`.
- **Output**: evaluation results are saved as a CSV file to the `evaluation/evaluation_results/` directory. The output filename is derived from the input PKL name with an `_evaluated` suffix (e.g., `all_models_result_other_evaluated.csv`).
- **Workflow**: the script reads each sample, looks up the corresponding ground-truth answer from `statformbench.pkl`, computes the metrics (JCV, PV, RV, ACC@1st, ACC@2nd, VRI), and writes the annotated results to CSV.

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
