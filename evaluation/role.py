def dict_to_list(data):
    return [key + value for key, values in data.items() for value in values]

def calculate_role_accuracy(answer, result):
    """
    计算answer["variable"]各变量对应角色（answer["role"]）在result中被判断正确的比例
    
    Args:
        answer (dict): 包含正确答案的字典，包含role字段
        result (dict): 模型预测结果的字典，包含role字段
    
    Returns:
        float: 角色判断的正确率，范围0-1
    """
    # 检查answer和result是否都包含role字段
    if "role" not in answer or "role" not in result:
        return 0.0
    
    answer_role = answer.get("role", {})
    result_role = result.get("role", {})
    
    # 情况1：如果answer["role"]和result["role"]均为空字典，则视为全部判断正确
    if not answer_role and not result_role:
        return 1.0
    
    # 情况2：如果result["role"]不为空但answer["role"]为空视为全部判断错误
    if result_role and not answer_role:
        return 0.0
    
    # 情况3：正常计算正确率
    total_variables = 0
    correct_roles = 0

    answer_v = dict_to_list(answer.get("variable", {}))
    result_v = dict_to_list(result.get("variable", {}))
    answer_r = dict_to_list(answer.get("role", {}))
    result_r = dict_to_list(result.get("role", {}))

    total_variables = len(answer_v)

    for i,r in enumerate(answer_r):
        if answer_v[i] not in result_v:
            continue
        else:
            idx=result_v.index(answer_v[i])
            if r == result_r[idx]:
                correct_roles += 1
    
    # 计算正确率
    if total_variables == 0:
        return 1.0
    else:
        return correct_roles / total_variables


def test_role_accuracy():
    """
    测试角色判断正确率计算函数
    """
    # 测试用例1：两者都为空字典
    answer1 = {"role": {}, "variable": {}}
    result1 = {"role": {}, "variable": {}}
    print(f"测试用例1（均为空字典）: {calculate_role_accuracy(answer1, result1)}")
    
    # 测试用例2：result不为空但answer为空
    answer2 = {"role": {}, "variable": {"LLM.pkl": ["Text", "Label"]}}
    result2 = {"role": {"LLM.pkl": ["independent", "dependent"]}, "variable": {"LLM.pkl": ["Text", "Label"]}}
    print(f"测试用例2（result不为空但answer为空）: {calculate_role_accuracy(answer2, result2)}")
    
    # 测试用例3：全部正确
    answer3 = {
        "role": {"LLM.pkl": ["independent", "dependent"],"LLM2.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"],"LLM2.pkl": ["A", "B"]}
    }
    result3 = {
        "role": {"LLM.pkl": ["independent", "dependent"],"LLM2.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"],"LLM2.pkl": ["A", "B"]}
    }
    print(f"测试用例3（全部正确）: {calculate_role_accuracy(answer3, result3)}")
    
    # 测试用例4：部分正确
    answer4 = {
        "role": {"LLM.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    result4 = {
        "role": {"LLM.pkl": ["independent", "independent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    print(f"测试用例4（部分正确）: {calculate_role_accuracy(answer4, result4)}")
    
    # 测试用例5：完全错误
    answer5 = {
        "role": {"LLM.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    result5 = {
        "role": {"LLM.pkl": ["dependent", "independent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    print(f"测试用例5（完全错误）: {calculate_role_accuracy(answer5, result5)}")


if __name__ == "__main__":
    test_role_accuracy()