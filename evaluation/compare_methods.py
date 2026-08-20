import csv
import os


def load_method_hierarchy():
    """
    加载sta.csv文件，返回method到hierarchy1的映射
    """
    method_hierarchy = {}
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'sta.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 检查行是否有效
            if 'hierarchy2' in row and 'hierarchy1' in row:
                method = row['hierarchy2'].strip() if row['hierarchy2'] else ''
                hierarchy = row['hierarchy1'].strip() if row['hierarchy1'] else ''
                if method and hierarchy:
                    method_hierarchy[method] = hierarchy
    
    return method_hierarchy



def compare_methods0(a, b):
    """
    严格匹配：当且仅当a和b完全相等时返回1，否则返回0
    
    Args:
        a (str): 第一个方法字符串
        b (str): 第二个方法字符串
    
    Returns:
        int: 1表示完全相同，0表示不同
    """
    return 1 if a == b else 0



def compare_methods1(a, b):
    """
    比较两个方法字符串a和b，根据规则返回相应的值
    
    Args:
        a (str): 第一个方法字符串
        b (str): 第二个方法字符串
    
    Returns:
        float: 根据规则返回0、0.5或1
    """
    # 加载方法到层级的映射
    method_hierarchy = load_method_hierarchy()
    
    # 检查a和b是否存在于hierarchy2中
    a_exists = a in method_hierarchy
    b_exists = b in method_hierarchy
    
    # 规则1: 如果a或b不存在，返回0
    if not a_exists or not b_exists:
        return 0
    
    # 规则2: 如果a和b对应的hierarchy1相同
    if method_hierarchy[a] == method_hierarchy[b]:
        return 1
    
    # 其他情况返回0
    return 0


def batch_compare(input_pairs, output_file=None):
    """
    批量比较方法对
    
    Args:
        input_pairs (list): 方法对列表，每个元素是(a, b)元组
        output_file (str, optional): 输出文件路径
    
    Returns:
        list: 比较结果列表
    """
    results = []
    
    for a, b in input_pairs:
        score = compare_methods1(a, b)
        results.append({
            'a': a,
            'b': b,
            'score': score
        })
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['a', 'b', 'score'])
            writer.writeheader()
            writer.writerows(results)
        print(f"批量比较结果已保存到 {output_file}")
    
    return results


if __name__ == "__main__":
    # 测试示例
    test_cases = [
        ("离散型变量分布", "离散型变量分布"),  # 应该返回1
        ("离散型变量分布", "连续型变量分布"),  # 应该返回0.5（同属于数据可视化）
        ("离散型变量分布", "回归系数显著性与方向解读"),  # 应该返回0（不同层级）
        ("离散型变量分布", "不存在的方法"),  # 应该返回0（b不存在）
        ("不存在的方法", "离散型变量分布"),  # 应该返回0（a不存在）
        ("不存在的方法1", "不存在的方法2"),  # 应该返回0（都不存在）
    ]
    
    print("测试比较方法：")
    for a, b in test_cases:
        score = compare_methods1(a, b)
        print(f"{a} vs {b} = {score}")
    
    # 测试批量比较
    print("\n测试批量比较：")
    batch_results = batch_compare(test_cases, 'compare_results.csv')
    for result in batch_results:
        print(result)