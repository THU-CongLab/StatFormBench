# statformbench

statformbench is a benchmark dataset designed to evaluate the ability of Large Language Models (LLMs) in **Statistical Problem Formulation**. This benchmark provides a comprehensive framework for assessing how well LLMs can understand and formulate statistical analysis problems from natural language descriptions.

## Dataset Overview

statformbench contains carefully curated statistical problem descriptions paired with structured output formats, enabling systematic evaluation of LLMs' capability to:
- Parse natural language statistical questions
- Identify appropriate statistical methods
- Extract relevant variables and their roles
- Generate structured representations of statistical analysis plans

## Project Structure

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
├── sta.csv              # Supplementary data for Classification
└── README.md            # This file
```

## Usage

### Running the Evaluation

```bash
python evaluation/evaluate_combined.py [optional: csv_path]
```

If no CSV path is provided, the script will use the default path: `results/all_models_result.csv`

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| JCV | Jaccard Coefficient - measures variable set similarity |
| PV | Precision - proportion of predicted variables that are correct |
| RV | Recall - proportion of correct variables that are predicted |
| ACC@1st | Method accuracy with relaxed matching |
| ACC@2nd | Method accuracy with strict exact matching |
| VRI | Variable Role Consistency - matching variable roles |

## Data Format

The benchmark expects model outputs in JSON format with the following structure:
```json
{
  "category": "statistical_method_name",
  "variables": {
    "variable_name": {
      "value": "variable_value",
      "role": "variable_role"
    }
  }
}
```

## Requirements

- Python 3.8+
- openai
- pandas
- numpy

Install dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is intended for research purposes. Please refer to the original dataset license for usage restrictions.

