import pandas as pd
import json
import os
import sys
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt import prompt_evaluate0
from api_info import api_key, base_url
from extract_last_json_safe import extract_last_json_safe


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_evaluation_data():
    """加载评估样本数据"""
    csv_path = os.path.join(os.path.dirname(__file__), 'evaluation_results', 'all_models_result_evaluated.csv')
    logger.info(f"加载评估样本文件: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"成功加载 {len(df)} 个样本")
    return df


def process_data_description(data_description):
    """处理data_description_2字段，仅保留关键信息"""
    if not data_description:
        return data_description
    
    # 检查是否为字典结构
    if isinstance(data_description, dict):
        # 针对每个数据集进行处理
        processed_description = {}
        for dataset_name, dataset_info in data_description.items():
            if isinstance(dataset_info, dict):
                # 仅保留指定的四个字段
                processed_dataset = {}
                if '数据类型' in dataset_info:
                    processed_dataset['数据类型'] = dataset_info['数据类型']
                if '数据形状' in dataset_info:
                    processed_dataset['数据形状'] = dataset_info['数据形状']
                if '变量名' in dataset_info:
                    processed_dataset['变量名'] = dataset_info['变量名']
                if '基本统计信息' in dataset_info:
                    processed_dataset['基本统计信息'] = dataset_info['基本统计信息']
                processed_description[dataset_name] = processed_dataset
            else:
                processed_description[dataset_name] = dataset_info
        return processed_description
    return data_description


def evaluate_with_llm(question_description, output_json, model_name="gpt-5-mini"):
    """
    调用大语言模型进行评估
    
    Args:
        question_description (str): 问题描述（JSON格式字符串）
        output_json (str): 待评估统计模型（JSON格式字符串）
        model_name (str): 使用的模型名称
    
    Returns:
        tuple: (evaluation_result, token_usage_dict)
            - evaluation_result: 解析后的评估结果字典或None
            - token_usage_dict: 包含input_tokens, output_tokens, total_tokens的字典
    """
    try:
        # 解析question_description为字典
        try:
            input_data = json.loads(question_description)
        except:
            input_data = {}
        
        # 检查并处理data_description_2字段
        if 'data_description_2' in input_data:
            data_description_2 = input_data['data_description_2']
            # 计算字符总数
            data_desc_str = json.dumps(data_description_2, ensure_ascii=False)

            #logger.info(f"检测到data_description_2字段过长（{len(data_desc_str)}字符），进行处理...")
                # 处理data_description_2字段
            processed_data_description = process_data_description(data_description_2)
                # 检查处理后的长度
            processed_str = json.dumps(processed_data_description, ensure_ascii=False)
            logger.info(f"处理后长度：{len(processed_str)}字符")
                # 更新input_data
            input_data['data_description_2'] = processed_data_description
                # 重新转换为JSON字符串
            question_description = json.dumps(input_data, ensure_ascii=False, indent=2)
        
        # 构建完整的prompt
        prompt = f"{prompt_evaluate0}\n\n问题描述 (JSON):\n{question_description}\n\n待评估统计模型 (JSON):\n{output_json}\n\n请按照要求的JSON格式输出评审报告："
        
        # 调用OpenAI API
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一位经验丰富的统计学专家和评审人。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        # 提取模型输出
        output = response.choices[0].message.content.strip()
        
        # 获取token使用量
        token_usage = {
            'input_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') and response.usage else 0,
            'output_tokens': response.usage.completion_tokens if hasattr(response, 'usage') and response.usage else 0,
            'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        }
        
        # 解析JSON输出
        result = extract_last_json_safe(output)
        
        return result, token_usage
        
    except Exception as e:
        logger.error(f"LLM评估失败: {e}")
        return None, {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}


def validate_evaluation_result(result):
    """
    验证模型输出是否符合要求的格式
    
    Args:
        result: 解析后的评估结果
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if result is None:
        return False, "无法解析JSON输出"
    
    if not isinstance(result, dict):
        return False, "输出不是字典格式"
    
    # 检查必需字段
    required_fields = ['total_score', 'scores', 'comment']
    for field in required_fields:
        if field not in result:
            return False, f"缺少必需字段: {field}"
    
    # 检查scores字段
    if not isinstance(result['scores'], dict):
        return False, "scores字段不是字典格式"
    
    required_score_fields = ['variable_role_abstraction', 'method_abstraction']
    for field in required_score_fields:
        if field not in result['scores']:
            return False, f"scores缺少必需字段: {field}"
    
    # 检查分数范围
    try:
        total_score = int(result['total_score'])
        if not (0 <= total_score <= 10):
            return False, f"total_score超出范围(0-10): {total_score}"
        
        var_score = int(result['scores']['variable_role_abstraction'])
        if not (0 <= var_score <= 5):
            return False, f"variable_role_abstraction超出范围(0-5): {var_score}"
        
        method_score = int(result['scores']['method_abstraction'])
        if not (0 <= method_score <= 5):
            return False, f"method_abstraction超出范围(0-5): {method_score}"
    except (ValueError, TypeError) as e:
        return False, f"分数格式错误: {e}"
    
    return True, None


def process_single_sample(row_data):
    """
    处理单个样本的评估，支持重试机制
    
    Args:
        row_data (tuple): (index, row) 样本索引和数据
    
    Returns:
        dict: 评估结果
    """
    idx, row = row_data
    sample_key = row['sample_key']
    model_name = row['model_name']
    error_type = row['error_type']
    
    logger.info(f"处理样本 {idx}: sample_key={sample_key}, model={model_name}, error_type={error_type}")
    
    # 初始化结果
    result = {
        'sample_key': sample_key,
        'model_name': model_name,
        'input_data': row['input_data'],
        'output_json': row['output_json'],
        'total_score': 0,
        'variable_role_abstraction': 0,
        'method_abstraction': 0,
        'comment': '无',
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0,
        'evaluation_error': None
    }
    
    # 检查error_type
    if error_type != 'successful':
        logger.info(f"样本 {idx} 的error_type不为successful，跳过LLM评估")
        result['evaluation_error'] = f"error_type={error_type}，无需评估"
        return result
    
    # 重试机制：最多尝试5次
    max_retries = 5
    question_description = row['input_data']
    output_json = row['output_json']
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"样本 {idx} 第 {attempt}/{max_retries} 次评估尝试")
        
        try:
            eval_result, token_usage = evaluate_with_llm(question_description, output_json)
            
            # 更新token使用量（累加）
            result['input_tokens'] += token_usage['input_tokens']
            result['output_tokens'] += token_usage['output_tokens']
            result['total_tokens'] += token_usage['total_tokens']
            
            # 验证结果
            is_valid, error_message = validate_evaluation_result(eval_result)
            
            if is_valid:
                # 评估成功，更新结果并跳出循环
                result['total_score'] = int(eval_result['total_score'])
                result['variable_role_abstraction'] = int(eval_result['scores']['variable_role_abstraction'])
                result['method_abstraction'] = int(eval_result['scores']['method_abstraction'])
                result['comment'] = eval_result['comment']
                result['evaluation_error'] = None
                logger.info(f"样本 {idx} 第 {attempt} 次评估成功: total_score={result['total_score']}")
                break
            else:
                # 验证失败，记录错误
                result['evaluation_error'] = f"第 {attempt} 次尝试失败 - 结果验证失败: {error_message}"
                logger.warning(f"样本 {idx} 第 {attempt} 次评估验证失败: {error_message}")
                
                # 如果还有重试机会，继续下一次尝试
                if attempt < max_retries:
                    logger.info(f"样本 {idx} 将进行第 {attempt + 1} 次重试")
                else:
                    logger.error(f"样本 {idx} 已达到最大重试次数 {max_retries}，评估失败")
        
        except Exception as e:
            # 异常处理
            result['evaluation_error'] = f"第 {attempt} 次尝试失败 - 评估异常: {str(e)}"
            logger.error(f"样本 {idx} 第 {attempt} 次评估异常: {e}")
            
            # 如果还有重试机会，继续下一次尝试
            if attempt < max_retries:
                logger.info(f"样本 {idx} 将进行第 {attempt + 1} 次重试")
            else:
                logger.error(f"样本 {idx} 已达到最大重试次数 {max_retries}，评估失败")
    
    return result


def save_batch_results(results, is_final=False, filename='evaluated0.csv'):
    """保存批次结果到文件，追加模式"""
    if not results:
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 确定保存路径
    output_dir = os.path.join(os.path.dirname(__file__), 'evaluation_results')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    # 追加模式保存数据
    if os.path.exists(output_path):
        # 文件已存在，追加模式写入（不写入表头）
        df.to_csv(output_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        # 文件不存在，创建新文件并写入表头
        df.to_csv(output_path, mode='w', header=True, index=False, encoding='utf-8-sig')
    
    if is_final:
        logger.info(f"\n最终结果已保存到: {output_path}")
        # 读取文件统计总行数
        try:
            final_df = pd.read_csv(output_path)
            logger.info(f"总记录数: {len(final_df)}")
        except:
            logger.info(f"本次保存 {len(results)} 条记录")
    else:
        logger.info(f"已追加保存 {len(results)} 条记录到 {output_path}")


def show_statistics(final_df):
    """显示评估统计信息"""
    logger.info("\n" + "=" * 60)
    logger.info("评估完成统计")
    logger.info("=" * 60)
    
    # 统计信息
    successful_evaluations = len(final_df[final_df['evaluation_error'].isna()])
    failed_evaluations = len(final_df[final_df['evaluation_error'].notna()])
    
    logger.info(f"总样本数: {len(final_df)}")
    logger.info(f"成功评估: {successful_evaluations}")
    logger.info(f"评估失败: {failed_evaluations}")
    
    # 分数统计
    if successful_evaluations > 0:
        logger.info("\n分数统计:")
        logger.info(f"total_score - 均值: {final_df['total_score'].mean():.2f}, 标准差: {final_df['total_score'].std():.2f}")
        logger.info(f"variable_role_abstraction - 均值: {final_df['variable_role_abstraction'].mean():.2f}, 标准差: {final_df['variable_role_abstraction'].std():.2f}")
        logger.info(f"method_abstraction - 均值: {final_df['method_abstraction'].mean():.2f}, 标准差: {final_df['method_abstraction'].std():.2f}")
    
    # Token使用统计
    total_input_tokens = final_df['input_tokens'].sum()
    total_output_tokens = final_df['output_tokens'].sum()
    total_tokens = final_df['total_tokens'].sum()
    
    logger.info(f"\nToken使用统计:")
    logger.info(f"总输入Tokens: {total_input_tokens}")
    logger.info(f"总输出Tokens: {total_output_tokens}")
    logger.info(f"总Tokens: {total_tokens}")
    
    # 显示前几条结果
    logger.info("\n前5条评估结果:")
    preview_columns = ['sample_key', 'model_name', 'total_score', 'variable_role_abstraction', 'method_abstraction']
    logger.info("\n" + str(final_df[preview_columns].head()))


def load_processed_samples(filename='evaluated0_newdata.csv'):
    """加载已处理的样本，用于断点续传"""
    output_path = os.path.join(os.path.dirname(__file__), 'evaluation_results', filename)
    processed_samples = set()
    
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path)
            # 使用sample_key和model_name的组合作为唯一标识
            # 统一转换为字符串类型进行比较，避免类型不匹配问题
            for _, row in existing_df.iterrows():
                sample_key = str(row['sample_key'])
                model_name = str(row['model_name'])
                processed_samples.add((sample_key, model_name))
            logger.info(f"检测到已处理的样本: {len(processed_samples)} 个")
        except Exception as e:
            logger.warning(f"读取已处理样本文件失败: {e}")
    
    return processed_samples


def main():
    """主函数，支持断点续传"""
    logger.info("=" * 60)
    logger.info("开始自动化评估")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 加载数据
    df = load_evaluation_data()
    total_samples = len(df)
    
    # 加载已处理的样本
    processed_samples = load_processed_samples(filename='evaluated0.csv')
    
    # 过滤出未处理的样本
    if processed_samples:
        # 创建标识列用于过滤，统一转换为字符串类型
        df['sample_id'] = df.apply(lambda row: (str(row['sample_key']), str(row['model_name'])), axis=1)
        # 过滤出未处理的样本
        df_unprocessed = df[~df['sample_id'].isin(processed_samples)].copy()
        # 删除临时列
        df_unprocessed = df_unprocessed.drop(columns=['sample_id'])
        
        skipped_count = len(df) - len(df_unprocessed)
        logger.info(f"跳过已处理样本: {skipped_count} 个")
        logger.info(f"待处理样本: {len(df_unprocessed)} 个")
        
        if len(df_unprocessed) == 0:
            logger.info("所有样本已处理完成！")
            df = pd.DataFrame()  # 空DataFrame
        else:
            df = df_unprocessed
    else:
        logger.info(f"待处理样本: {total_samples} 个")
    
    # 如果没有需要处理的样本，直接显示统计信息
    if len(df) == 0:
        logger.info("没有需要处理的样本，显示已有结果统计...")
        # 加载完整结果并显示统计信息
        output_path = os.path.join(os.path.dirname(__file__), 'evaluation_results', 'evaluated0.csv')
        if os.path.exists(output_path):
            final_df = pd.read_csv(output_path)
            show_statistics(final_df)
        return
    
    # 存储所有结果
    all_results = []
    batch_size = 50
    processed_count = 0
    remaining_samples = len(df)
    
    # 设置最大线程数
    max_workers = min(8, os.cpu_count() or 1)
    logger.info(f"使用 {max_workers} 个线程进行并行处理")
    
    # 准备样本数据
    sample_data = [(idx, row) for idx, row in df.iterrows()]
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_idx = {}
        for idx, row in sample_data:
            future = executor.submit(process_single_sample, (idx, row))
            future_to_idx[future] = idx
        
        # 处理完成的任务
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            
            try:
                result = future.result()
                all_results.append(result)
                processed_count += 1
                
                # 流式输出进度
                logger.info(f"进度: {processed_count}/{remaining_samples} - 样本 {result['sample_key']} - {result['model_name']} - 完成")
                
                # 每处理50个样本保存一次
                if len(all_results) >= batch_size:
                    save_batch_results(all_results, is_final=False, filename='evaluated0.csv')
                    all_results = []
                
            except Exception as e:
                logger.error(f"任务执行失败: 样本索引 {idx}, 错误: {e}")
    
    # 保存剩余的结果
    if all_results:
        save_batch_results(all_results, is_final=True, filename='evaluated0.csv')
    
    # 加载完整结果并显示统计信息
    output_path = os.path.join(os.path.dirname(__file__), 'evaluation_results', 'evaluated0.csv')
    if os.path.exists(output_path):
        final_df = pd.read_csv(output_path)
        show_statistics(final_df)


if __name__ == "__main__":
    main()