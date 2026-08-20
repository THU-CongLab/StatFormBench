import json
import pandas as pd
import pickle
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加评估模块路径
sys.path.append(os.path.dirname(__file__))

# 导入评估相关模块
from test_0 import evaluate_0
from var import jaccard_coefficient, calculate_ratio_set
from extract_last_json_safe import extract_last_json_safe
from compare_methods import compare_methods1


def load_combined_data():
    """加载statformbench.pkl文件，获取标准答案"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'statformbench.pkl')
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    return data


def evaluate_case_sample(row, combined_data):

    sample_key = row['sample_key']
    model_name = row['model_name']
    
    try:
        # 处理sample_key
        if pd.isna(sample_key):
            sample_key_str = ''
        elif isinstance(sample_key, (int, float)):
            sample_key_str = str(int(sample_key))
        else:
            sample_key_str = str(sample_key)
        
        # 获取question_description (input_data列)
        question_description = row['input_data']
        
        # 获取result (output_json列)
        result = row['output_json']
        
        # 获取answer (从combined_data中根据sample_key查找)
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
        
        # 调用evaluate_0进行评估
        eval_result = evaluate_0(question_description, result, answer)
        
        # 处理评估结果
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
    """评估source为book的样本，使用evaluatebook.py的逻辑"""
    sample_key = row['sample_key']
    output_json_str = row['output_json']
    
    # 检查output_json是否为字符串
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
    
    # 检查是否包含错误信息
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

    # 检查output_json是否为None
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
    
    # 检查是否有category和variables字段
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
    
    # 获取预测的category和variables
    pred_category = output_json.get('category', '')
    pred_variables = output_json.get('variables', {})
    
    # 处理sample_key
    if pd.isna(sample_key):
        sample_key_str = ''
    elif isinstance(sample_key, (int, float)):
        sample_key_str = str(int(sample_key))
    else:
        sample_key_str = str(sample_key)

    # 获取标签数据
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
    
    # 获取标签的category和variable
    # 注意：标签数据使用 'variable' (单数)，模型输出使用 'variables' (复数)
    label_category = label_record.get('output', {}).get('category', '')
    label_variable = label_record.get('output', {}).get('variable', {})
    
    # 计算ACC@2nd (精确匹配)
    acc_2nd = 1 if pred_category == label_category else 0
    
    # 计算ACC@1st (使用compare_methods1比较)
    try:
        acc_1st = compare_methods1(pred_category, label_category)
    except Exception as e:
        acc_1st = 0
    
    # 提取value字段用于变量比较
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

    # 计算JCV（Jaccard系数）
    try:
        jcv = jaccard_coefficient(pred_values, label_values)
    except Exception as e:
        jcv = 0

    # 计算PV（变量选取的精度）
    try:
        pv = calculate_ratio_set(pred_values, label_values)
    except Exception as e:
        pv = 0

    # 计算RV（变量选取的召回）
    try:
        rv = calculate_ratio_set(label_values, pred_values)
    except Exception as e:
        rv = 0

    # 计算VRI（变量角色一致性）
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
    """评估单个样本，根据source字段选择评估逻辑"""
    sample_key = row['sample_key']
    
    # 处理sample_key
    if pd.isna(sample_key):
        sample_key_str = ''
    elif isinstance(sample_key, (int, float)):
        sample_key_str = str(int(sample_key))
    else:
        sample_key_str = str(sample_key)

    # 从combined_data获取source字段
    source = 'case'  # 默认值
    if sample_key_str in combined_data:
        record = combined_data.get(sample_key_str)
        if isinstance(record, dict):
            source = record.get('source', 'case')
    
    # 根据source字段选择评估逻辑
    if source == 'book':
        return evaluate_book_sample(row, combined_data)
    else:  # case 或其他
        return evaluate_case_sample(row, combined_data)


def evaluate_csv_results(pkl_path):
    """评估PKL文件中的每个样本"""
    # 读取PKL文件
    df = pd.read_pickle(pkl_path)
    
    print(f"读取PKL文件: {pkl_path}")
    print(f"总行数: {len(df)}")
    
    # 加载标准答案数据
    combined_data = load_combined_data()
    print(f"加载combined_data.pkl完成，共 {len(combined_data)} 条记录")
    
    # 统计source分布
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
    
    print(f"\nsource分布统计:")
    print(f"  case样本数: {source_counts['case']}")
    print(f"  book样本数: {source_counts['book']}")
    print(f"  未知样本数: {source_counts['unknown']}")
    
    # 存储评估结果
    evaluation_results = [None] * len(df)
    
    # 设置最大线程数
    max_workers = min(1, os.cpu_count() * 2)
    print(f"\n使用 {max_workers} 个线程进行并行处理")
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {}
        for idx, row in df.iterrows():
            future = executor.submit(evaluate_single_sample, row, combined_data)
            future_to_idx[future] = idx
        
        # 处理完成的任务
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            sample_key = df.loc[idx, 'sample_key']
            model_name = df.loc[idx, 'model_name']
            
            try:
                result = future.result()
                evaluation_results[idx] = result
                
                if result['error'] is None:
                    print(f"评估完成: 第 {idx+1}/{len(df)} 行 - sample_key={sample_key}, model={model_name}, error_type={result['error_type']}")
                else:
                    print(f"评估失败: 第 {idx+1}/{len(df)} 行 - sample_key={sample_key}, model={model_name}, error={result['error']}")
            except Exception as e:
                print(f"任务执行失败: 第 {idx+1}/{len(df)} 行 - sample_key={sample_key}, model={model_name}, error={e}")
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
    
    # 将评估结果转换为DataFrame（过滤掉None值）
    default_error = {
        'error_type': 'no_result',
        'JCV': 0, 'PV': 0, 'RV': 0,
        'ACC@2nd': 0, 'ACC@1st': 0, 'VRI': 0,
        'error': 'No evaluation result'
    }
    evaluation_results = [r if r is not None else default_error for r in evaluation_results]
    eval_df = pd.DataFrame(evaluation_results)
    
    # 将评估结果添加到原始DataFrame
    df['error_type'] = eval_df['error_type']
    df['JCV'] = eval_df['JCV']
    df['PV'] = eval_df['PV']
    df['RV'] = eval_df['RV']
    df['ACC@2nd'] = eval_df['ACC@2nd']
    df['ACC@1st'] = eval_df['ACC@1st']
    df['VRI'] = eval_df['VRI']
    df['evaluation_error'] = eval_df['error']
    
    # 保存结果到evaluation_results目录
    output_dir = os.path.join(os.path.dirname(__file__), 'evaluation_results')
    os.makedirs(output_dir, exist_ok=True)
    
    pkl_filename = os.path.basename(pkl_path)
    name_without_ext = os.path.splitext(pkl_filename)[0]
    output_path = os.path.join(output_dir, f'{name_without_ext}_evaluated.csv')
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n评估完成！结果已保存到: {output_path}")
    print(f"成功评估: {len(df[df['evaluation_error'].isna()])} 条")
    print(f"评估失败: {len(df[df['evaluation_error'].notna()])} 条")
    
    # 显示错误类型统计
    print("\n错误类型统计:")
    print(df['error_type'].value_counts())
    
    # 显示评估分数统计（统一字段）
    print("\n评估分数统计 (JCV, PV, RV, ACC@1st, ACC@2nd, VRI):")
    valid_df = df[(df['JCV'].notna()) | (df['PV'].notna()) | (df['RV'].notna())]
    if len(valid_df) > 0:
        print(valid_df[['JCV', 'PV', 'RV', 'ACC@2nd', 'ACC@1st', 'VRI']].describe())
    
    return df


if __name__ == "__main__":
    # 默认评估路径（PKL文件）
    default_pkl_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'all_models_result_other.pkl')
    
    # 检查是否提供了命令行参数
    if len(sys.argv) > 1:
        pkl_path = sys.argv[1]
    else:
        pkl_path = default_pkl_path
    
    print("=" * 70)
    print("综合评估脚本")
    print("=" * 70)
    print(f"评估文件: {pkl_path}")
    print("=" * 70)
    
    # 运行评估
    result_df = evaluate_csv_results(pkl_path)
    
    # 显示前几条结果
    print("\n前5条评估结果:")
    print(result_df[['sample_key', 'model_name', 'error_type', 'JCV', 'PV', 'RV', 'ACC@2nd', 'ACC@1st', 'VRI']].head())