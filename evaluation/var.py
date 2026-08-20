import pickle
import pandas as pd
import numpy as np
import random
import re
import json

def jaccard_coefficient(A, B):
    """
    计算集合 A 和 B 的 Jaccard 系数。
    
    参数:
        A (set): 集合 A
        B (set): 集合 B
    
    返回:
        float: Jaccard 系数
    """
    if not A and not B:
        return 1.0
    elif not A or not B:
        return 0.0
    else:
        intersection = len(A & B)
        union = len(A | B)
        return intersection / union

def calculate_ratio_set(A, B):
    """
    计算A集合中元素在B集合中存在的比例（使用集合操作）
    
    参数:
        A: 可迭代对象，如列表、元组、集合等
        B: 可迭代对象，如列表、元组、集合等
    
    返回:
        float: 存在比例 (0.0 到 1.0 之间)
    """
    # 转换为集合以进行高效查找
    set_A = set(A)
    set_B = set(B)
    
    # 计算A中存在于B的元素数量
    common_count = len(set_A & set_B)
    
    # 计算比例
    if len(set_A) == 0:
        return 0.0  # 处理空集合的情况
    
    return common_count / len(set_A)