import json
import pandas as pd
import pickle
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add evaluation module path
sys.path.append(os.path.dirname(__file__))

# Import evaluation-related modules
from evaluate_case import evaluate_0
from variable_metrics import jaccard_coefficient, calculate_ratio_set
from json_utils import extract_last_json_safe
from compare_methods import compare_methods1


def load_combined_data():
    """Load statformbench.pkl file to get ground truth answers"""
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'statformbench.pkl')
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    return data


def evaluate_case_sample(row, combined_data):

    sample_key = row['sample_key']
    model_name = row['model_name']
    
    try:
        # Process sample_key
        if pd.isna(sample_key):
            sample_key_str = ''
        elif isinstance(sample_key, (int, float)):
            sample_key_str = str(int(sample_key))
        else:
            sample_key_str = str(sample_key)
        
        # Get question_description (input_data column)
        question_description = row['input_data']
        
        # Get result (output_json column)
        result = row['output_json']
        
        # Get answer (look up from combined_data by sample_key)
        if sample_key_str in combined_data:
            answer_data = combined_data[sample_key_str]
            if isinstance(answer_data, dict):
                if 'category' in answer_data and 'variable' in answer_data:
                    answer = answer_data
                elif 'output' in answer_data and isinstance(answer_data['output'], dict):
                    output_data = answer_data['output']
                    if 'category' in output_data and 'variable' in output_data:
                        answer = output_data
                    else:
                        return {
                            'error_type': 'missing_fields',
                            'JCV': 0,
                            'PV': 0,
                            'RV': 0,
                            'ACC@2nd': 0,
                            'ACC@1st': 0,
                            'VRI': 0,
                            'error': f'Missing fields in output for sample_key {sample_key_str}'
                        }
                else:
                    return {
                        'error_type': 'invalid_format',
                        'JCV': 0,
                        'PV': 0,
                        'RV': 0,
                        'ACC@2nd': 0,
                        'ACC@1st': 0,
                        'VRI': 0,
                        'error': f'Invalid data format for sample_key {sample_key_str}'
                    }
            else:
                return {
                    'error_type': 'invalid_format',
                    'JCV': 0,
                    'PV': 0,
                    'RV': 0,
                    'ACC@2nd': 0,
                    'ACC@1st': 0,
                    'VRI': 0,
                    'error': f'Invalid data format for sample_key {sample_key_str}'
                }
        else:
            return {
                'error_type': 'sample_not_found',
                'JCV': 0,
                'PV': 0,
                'RV': 0,
                'ACC@2nd': 0,
                'ACC@1st': 0,
                'VRI': 0,
                'error': f'sample_key {sample_key_str} not found'
            }
        
        # Call evaluate_0 for evaluation
        eval_result = evaluate_0(question_description, result, answer)
        
        # Process evaluation results
        if isinstance(eval_result, list):
            if len(eval_result) >= 7:
                error_type, variable_score, precision_score, recall_score, method_score2, method_score1, role_score = eval_result

                return {
                    'error_type': error_type,
                    'JCV': variable_score,
                    'PV': precision_score,
                    'RV': recall_score,
                    'ACC@2nd': method_score2,
                    'ACC@1st': method_score1,
                    'VRI': role_score,
                    'error': None
                }
            else:
                return {
                    'error_type': 'invalid_eval_result',
                    'JCV': 0,
                    'PV': 0,
                    'RV': 0,
                    'ACC@2nd': 0,
                    'ACC@1st': 0,
                    'VRI': 0,
                    'error': f'Invalid evaluation result format: {eval_result}'
                }
        else:
            return {
                'error_type': 'invalid_eval_result',
                'JCV': 0,
                'PV': 0,
                'RV': 0,
                'ACC@2nd': 0,
                'ACC@1st': 0,
                'VRI': 0,
                'error': f'Invalid evaluation result type: {type(eval_result)}'
            }
        
    except Exception as e:
        return {
            'error_type': 'evaluation_error',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': str(e)
        }


def evaluate_book_sample(row, combined_data):
    """Evaluate samples with source='book'"""
    sample_key = row['sample_key']
    output_json_str = row['output_json']
    
    # Check if output_json is a string
    if not isinstance(output_json_str, str):
        return {
            'error_type': 'output_not_string',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': 'output_json is not string'
        }
    
    # Check if it contains error message
    if output_json_str.startswith("错误:") or output_json_str.startswith("Error:"):
        return {
            'error_type': 'output_error',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': 'output_json contains error message'
        }

    output_json = extract_last_json_safe(output_json_str)

    # Check if output_json is None
    if output_json is None:
        return {
            'error_type': 'output_empty',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': 'output_json is empty'
        }
    
    # Check if category and variables fields exist
    if 'category' not in output_json or 'variables' not in output_json:
        return {
            'error_type': 'missing_fields',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': 'output_json missing category or variables field'
        }
    
    # Get predicted category and variables
    pred_category = output_json.get('category', '')
    pred_variables = output_json.get('variables', {})
    
    # Process sample_key
    if pd.isna(sample_key):
        sample_key_str = ''
    elif isinstance(sample_key, (int, float)):
        sample_key_str = str(int(sample_key))
    else:
        sample_key_str = str(sample_key)

    # Get label data
    label_record = combined_data.get(sample_key_str)
    
    if label_record is None:
        return {
            'error_type': 'sample_not_found',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': f'sample_key {sample_key_str} not found'
        }
    
    # Get label category and variable
    # Note: label data uses 'variable' (singular), model output uses 'variables' (plural)
    label_category = label_record.get('output', {}).get('category', '')
    label_variable = label_record.get('output', {}).get('variable', {})
    
    # Calculate ACC@2nd (exact match)
    acc_2nd = 1 if pred_category == label_category else 0
    
    # Calculate ACC@1st (using compare_methods1)
    try:
        acc_1st = compare_methods1(pred_category, label_category)
    except Exception as e:
        acc_1st = 0
    
    # Extract value field for variable comparison
    pred_values = set()
    try:
        for var_key, var_data in pred_variables.items():
            value = var_data.get('value')
            if isinstance(value, dict):
                pred_values.add(json.dumps(value, sort_keys=True))
            elif isinstance(value, list):
                pred_values.add(json.dumps(value, sort_keys=True))
            else:
                pred_values.add(str(value))
    except Exception as e:
        return {
            'error_type': 'pred_variables_error',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': f'Error processing pred_variables: {e}'
        }

    label_values = set()
    try:
        for var_key, var_data in label_variable.items():
            value = var_data.get('value')
            if isinstance(value, dict):
                label_values.add(json.dumps(value, sort_keys=True))
            elif isinstance(value, list):
                label_values.add(json.dumps(value, sort_keys=True))
            else:
                label_values.add(str(value))
    except Exception as e:
        return {
            'error_type': 'label_variable_error',
            'JCV': 0,
            'PV': 0,
            'RV': 0,
            'ACC@2nd': 0,
            'ACC@1st': 0,
            'VRI': 0,
            'error': f'Error processing label_variable: {e}'
        }

    # Calculate JCV (Jaccard coefficient)
    try:
        jcv = jaccard_coefficient(pred_values, label_values)
    except Exception as e:
        jcv = 0

    # Calculate PV (precision)
    try:
        pv = calculate_ratio_set(pred_values, label_values)
    except Exception as e:
        pv = 0

    # Calculate RV (recall)
    try:
        rv = calculate_ratio_set(label_values, pred_values)
    except Exception as e:
        rv = 0

    # Calculate VRI (variable role consistency)
    matching_count = 0
    total_label_vars = len(label_variable)

    try:
        for label_var_key, label_var_data in label_variable.items():
            label_value = label_var_data.get('value')
            label_role = label_var_data.get('role')
            
            for pred_var_key, pred_var_data in pred_variables.items():
                pred_value = pred_var_data.get('value')
                pred_role = pred_var_data.get('role')
                
                if isinstance(label_value, dict) and isinstance(pred_value, dict):
                    value_match = json.dumps(label_value, sort_keys=True) == json.dumps(pred_value, sort_keys=True)
                elif isinstance(label_value, list) and isinstance(pred_value, list):
                    value_match = json.dumps(label_value, sort_keys=True) == json.dumps(pred_value, sort_keys=True)
                else:
                    value_match = str(label_value) == str(pred_value)
                
                if value_match:
                    if label_role == pred_role:
                        matching_count += 1
                    break
    except Exception as e:
        matching_count = 0
        total_label_vars = 1

    vri = matching_count / total_label_vars if total_label_vars > 0 else 0.0

    return {
        'error_type': 'success',
        'JCV': jcv,
        'PV': pv,
        'RV': rv,
        'ACC@2nd': acc_2nd,
        'ACC@1st': acc_1st,
        'VRI': vri,
        'error': None
    }


def evaluate_single_sample(row, combined_data):
    """Evaluate a single sample, selecting logic based on source field"""
    sample_key = row['sample_key']
    
    # Process sample_key
    if pd.isna(sample_key):
        sample_key_str = ''
    elif isinstance(sample_key, (int, float)):
        sample_key_str = str(int(sample_key))
    else:
        sample_key_str = str(sample_key)

    # Get source field from combined_data
    source = 'case'  # default value
    if sample_key_str in combined_data:
        record = combined_data.get(sample_key_str)
        if isinstance(record, dict):
            source = record.get('source', 'case')
    
    # select evaluation logic based on source field
    if source == 'book':
        return evaluate_book_sample(row, combined_data)
    else:  # case or other
        return evaluate_case_sample(row, combined_data)


def evaluate_csv_results(pkl_path):
    """Evaluate each sample in the PKL file"""
    # Reading PKL file
    df = pd.read_pickle(pkl_path)
    
    print(f"Reading PKL file: {pkl_path}")
    print(f"Total rows: {len(df)}")
    
    # Load ground truth data
    combined_data = load_combined_data()
    print(f"Loaded combined_data.pkl, total {len(combined_data)} records")
    
    # Count source distribution
    source_counts = {'case': 0, 'book': 0, 'unknown': 0}
    for sample_key in df['sample_key']:
        if pd.isna(sample_key):
            sample_key_str = ''
        elif isinstance(sample_key, (int, float)):
            sample_key_str = str(int(sample_key))
        else:
            sample_key_str = str(sample_key)
        
        if sample_key_str in combined_data:
            record = combined_data.get(sample_key_str)
            if isinstance(record, dict):
                source = record.get('source', 'case')
                if source == 'book':
                    source_counts['book'] += 1
                else:
                    source_counts['case'] += 1
            else:
                source_counts['case'] += 1
        else:
            source_counts['unknown'] += 1
    
    print(f"\nSource distribution statistics:")
    print(f"  case samples: {source_counts['case']}")
    print(f"  book samples: {source_counts['book']}")
    print(f"  unknown samples: {source_counts['unknown']}")
    
    # Store evaluation results
    evaluation_results = [None] * len(df)
    
    # Set max worker threads
    max_workers = min(1, os.cpu_count() * 2)
    print(f"\nUsing {max_workers} threads for parallel processing")
    
    # Use thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {}
        for idx, row in df.iterrows():
            future = executor.submit(evaluate_single_sample, row, combined_data)
            future_to_idx[future] = idx
        
        # Process completed tasks
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            sample_key = df.loc[idx, 'sample_key']
            model_name = df.loc[idx, 'model_name']
            
            try:
                result = future.result()
                evaluation_results[idx] = result
                
                if result['error'] is None:
                    print(f"Evaluation complete: row {idx+1}/{len(df)} - sample_key={sample_key}, model={model_name}, error_type={result['error_type']}")
                else:
                    print(f"Evaluation failed: row {idx+1}/{len(df)} - sample_key={sample_key}, model={model_name}, error={result['error']}")
            except Exception as e:
                print(f"Task execution failed: row {idx+1}/{len(df)} - sample_key={sample_key}, model={model_name}, error={e}")
                evaluation_results[idx] = {
                    'error_type': 'task_execution_error',
                    'JCV': 0,
                    'PV': 0,
                    'RV': 0,
                    'ACC@2nd': 0,
                    'ACC@1st': 0,
                    'VRI': 0,
                    'error': str(e)
                }
    
    # Convert evaluation results to DataFrame (filter out None values)
    default_error = {
        'error_type': 'no_result',
        'JCV': 0, 'PV': 0, 'RV': 0,
        'ACC@2nd': 0, 'ACC@1st': 0, 'VRI': 0,
        'error': 'No evaluation result'
    }
    evaluation_results = [r if r is not None else default_error for r in evaluation_results]
    eval_df = pd.DataFrame(evaluation_results)
    
    # Add evaluation results to original DataFrame
    df['error_type'] = eval_df['error_type']
    df['JCV'] = eval_df['JCV']
    df['PV'] = eval_df['PV']
    df['RV'] = eval_df['RV']
    df['ACC@2nd'] = eval_df['ACC@2nd']
    df['ACC@1st'] = eval_df['ACC@1st']
    df['VRI'] = eval_df['VRI']
    df['evaluation_error'] = eval_df['error']
    
    # Save results to evaluation_results directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results')
    os.makedirs(output_dir, exist_ok=True)
    
    pkl_filename = os.path.basename(pkl_path)
    name_without_ext = os.path.splitext(pkl_filename)[0]
    output_path = os.path.join(output_dir, f'{name_without_ext}_evaluated.csv')
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\nEvaluation complete! Results saved to: {output_path}")
    print(f"Successfully evaluated: {len(df[df['evaluation_error'].isna()])} records")
    print(f"Evaluation failed: {len(df[df['evaluation_error'].notna()])} records")
    
    # Show error type statistics
    print("\nError type statistics:")
    print(df['error_type'].value_counts())
    
    # Show evaluation score statistics (unified fields)
    print("\nEvaluation score statistics (JCV, PV, RV, ACC@1st, ACC@2nd, VRI):")
    valid_df = df[(df['JCV'].notna()) | (df['PV'].notna()) | (df['RV'].notna())]
    if len(valid_df) > 0:
        print(valid_df[['JCV', 'PV', 'RV', 'ACC@2nd', 'ACC@1st', 'VRI']].describe())
    
    return df


if __name__ == "__main__":
    # Default evaluation path (PKL file)
    default_pkl_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'all_models_result_other.pkl')
    
    # Check if command line argument is provided
    if len(sys.argv) > 1:
        pkl_path = sys.argv[1]
    else:
        pkl_path = default_pkl_path
    
    print("=" * 70)
    print("Comprehensive evaluation script")
    print("=" * 70)
    print(f"Evaluation file: {pkl_path}")
    print("=" * 70)
    
    # Run evaluation
    result_df = evaluate_csv_results(pkl_path)
    
    # Show first few results
    print("\nFirst 5 evaluation results:")
    print(result_df[['sample_key', 'model_name', 'error_type', 'JCV', 'PV', 'RV', 'ACC@2nd', 'ACC@1st', 'VRI']].head())