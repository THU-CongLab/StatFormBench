import openai
import json
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#from prompt import prompt_evaluate0
from api_info import api_key, base_url
from extract_last_json_safe import extract_last_json_safe

def check_dictionary_structure(data):
    """
    检查字典是否符合指定的评分结构
    
    参数:
        data: 要检查的字典
    
    返回:
        bool: 如果结构正确返回True，否则返回False
    """
    # 检查是否为字典
    if not isinstance(data, dict):
        return False
    
    # 检查必需的键是否存在
    required_keys = {"score", "dimension_scores", "comment"}
    if not all(key in data for key in required_keys):
        return False
    
    # 检查score的类型和范围
    if not isinstance(data["score"], (int, float)):
        return False
    
    # 检查dimension_scores是否为字典
    if not isinstance(data["dimension_scores"], dict):
        return False
    
    # 检查dimension_scores中的必需键
    required_dimensions = {"method_appropriateness", "process_logic", "comparison_with_reference"}
    dimension_scores = data["dimension_scores"]
    
    if not all(dim in dimension_scores for dim in required_dimensions):
        return False
    
    # 检查维度分数的类型
    for dim in required_dimensions:
        if not isinstance(dimension_scores[dim], (int, float)):
            return False
    
    # 检查comment的类型
    if not isinstance(data["comment"], str):
        return False
    
    return True


def evaluate_statistical_model(question_description, candidate_model, reference_model, model_name="gpt-5.2"):
    """
    调用大模型评估统计模型抽象结果
    
    Args:
        question_description (dict): 问题描述，包含background、data_description_1、question等
        reference_model (dict): 参考统计模型，包含method、variable、answer
        candidate_model (dict): 待评估统计模型，包含method、variable、answer
        model_name (str): 使用的模型名称
    
    Returns:
        dict: 评估结果，包含score、dimension_scores和comment
    """
    # 构建完整的prompt
    input_data = {
        "问题描述": question_description,
        "参考统计模型": reference_model,
        "待评估统计模型": candidate_model
    }
    
    prompt = f"{prompt_evaluate0}\n\n输入信息：\n{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\n请按照要求的JSON格式输出评审报告："
    
    # 调用OpenAI API
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "你是一位经验丰富的统计方法学专家和评审人"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1000
    )
    
    # 提取模型输出
    output = response.choices[0].message.content.strip()
    
    # 使用extract_last_json_safe提取完整的JSON
    result = extract_last_json_safe(output)
    
    if result is None or check_dictionary_structure(result)==False:
        return "unsuccessful"
    else:
        return result


def batch_evaluate(input_file, output_file, model_name="gpt-5"):
    """
    批量评估多个统计模型
    
    Args:
        input_file (str): 输入文件路径，包含多个评估案例
        output_file (str): 输出文件路径，保存评估结果
        model_name (str): 使用的模型名称
    """
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    results = []
    
    # 评估每个案例
    for i, case in enumerate(cases):
        print(f"评估案例 {i+1}/{len(cases)}...")
        
        try:
            question_description = case['question_description']
            reference_model = case['reference_model']
            candidate_model = case['candidate_model']
            
            # 调用评估函数
            result = evaluate_statistical_model(
                question_description, 
                reference_model, 
                candidate_model, 
                model_name
            )
            
            # 添加案例信息
            result['case_id'] = case.get('case_id', i+1)
            result['input'] = case
            
            results.append(result)
            
            # 添加延迟避免API限制
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"评估案例 {i+1} 失败: {e}")
            # 添加错误记录
            error_result = {
                'case_id': case.get('case_id', i+1),
                'error': str(e),
                'input': case
            }
            results.append(error_result)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"评估完成！结果已保存到 {output_file}")
    print(f"总共评估了 {len(results)} 个案例")
    
    return results


if __name__ == "__main__":
    # 测试示例
    test_question_description = {
        "background": "全球性别差异报告（GGGR）是一项旨在衡量各国在性别平等方面进展的报告。",
        "data_description_1": "数据由两个部分构成：(1) GGGR提供的各国综合得分和分项得分；(2) 世界银行提供的各国经济发展指标。",
        "question": "哪些因素对性别平等得分有显著影响？"
    }
    
    test_reference_model = {
        "category": "回归系数显著性与方向解读",
        "variable": {"gggr_data.pkl": ["gender_equality_score", "gdp_per_capita", "education_index"]},
        "answer": "使用多元线性回归模型，以性别平等得分为因变量，GDP per capita和教育指数为自变量，分析各因素对性别平等的影响方向和显著性。"
    }
    
    test_candidate_model = {
        "category": "连续值预测",
        "variable": {"gggr_data.pkl": ["gender_equality_score", "gdp_per_capita", "education_index"]},
        "answer": "使用多元线性回归模型，以性别平等得分为因变量，GDP per capita和教育指数为自变量，预测性别平等得分并分析各因素的影响。"
    }
    
    print("测试评估功能...")
    result = evaluate_statistical_model(
        test_question_description,
        test_reference_model,
        test_candidate_model
    )
    
    print("评估结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))