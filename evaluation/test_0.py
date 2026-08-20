import os
from extract_last_json_safe import extract_last_json_safe
from var import jaccard_coefficient, calculate_ratio_set
from compare_methods import compare_methods0, compare_methods1
from auto_m0 import evaluate_statistical_model
from role import calculate_role_accuracy

example_model_score={
  "score": 0,
  "dimension_scores": {
    "method_appropriateness": 0,
    "process_logic": 0,
    "comparison_with_reference": 0
  },
  "comment": "无"
}

def dict_to_set(data):
    return {key + value for key, values in data.items() for value in values}

def dict_to_list(data):
    return [key + value for key, values in data.items() for value in values]

def dict_structure_equal(dict1, dict2):
    """
    判断两个字典结构是否完全相同
    """
    try:
        # 判断key是否完全相同
        if dict1.keys() != dict2.keys():
            return False
        
        # 判断每个key对应的value是否都是列表且长度相同
        for key in dict1:
            val1, val2 = dict1[key], dict2[key]
            
            # 检查是否都是列表
            if not isinstance(val1, list) or not isinstance(val2, list):
                return False
            
            # 检查列表长度
            if len(val1) != len(val2):
                return False
        
        return True
    
    except (AttributeError, TypeError):
        # 处理输入不是字典的情况
        return False

def evaluate_0(question_description, result, answer):
    #answer是dict类型
    result=extract_last_json_safe(result)
    if result is None:
        return ["no_json",0 , 0 , 0 , 0 , 0, 0]
    elif not set(["category", "variable", "role"])==set(result.keys()):
        return ["false_json",0 , 0 , 0 , 0 , 0, 0]
    elif dict_structure_equal(result["role"], result["variable"])==False:
        return ["false_role",0 , 0 , 0 , 0 , 0, 0]
    else:
        variable_score=jaccard_coefficient(dict_to_set(result["variable"]), dict_to_set(answer["variable"]))
        precision_score=calculate_ratio_set(dict_to_set(result["variable"]), dict_to_set(answer["variable"]))
        recall_score=calculate_ratio_set(dict_to_set(answer["variable"]), dict_to_set(result["variable"]))
        role_score=calculate_role_accuracy(answer, result)
            
        method_score2=compare_methods0(result["category"], answer["category"])
        method_score1=compare_methods1(result["category"], answer["category"])
        
        #model_score=evaluate_statistical_model(question_description, result, answer)
        model_score=0
        if model_score =="unsuccessful":
            return ["unsuccessful_model_score",variable_score , precision_score , recall_score , method_score2 , method_score1,role_score]
        else:
            return ["successful",variable_score , precision_score , recall_score , method_score2 , method_score1,role_score]


if __name__ == '__main__':
    question_description='''
    {"background": "短视频的流行促使许多内容创作者和品牌寻求提高其视频的曝光率和互动率，特别是点赞数。本任务旨在探索影响短视频点赞数的因素，帮助内容创作者优化他们的短视频，以获得更好的用户反馈和互动。", "data_description_1": "数据集来源于短视频平台，包含6400条短视频记录，共11个变量，具体包括：序号（视频的唯一标识），作者编号（视频创作者的标识），点赞数（视频获得的点赞数量），评论数（视频的评论数量），分享数（视频被分享的次数），BGM（背景音乐），时长（视频时长），发布日期（视频发布的日期），发布时间（视频发布的具体时间），类别（视频的内容类别），标题字数（视频标题的字数）。", "data_description_2": {"data.pkl": {"数据类型": "DataFrame", "数据形状": "6400 行 × 11 列", "变量名": ["序号", "作者编号", "点赞数", "评论数", "分享数", "BGM", "时长", "发布日期", "发布时间", "类别", "标题字数"], "数据类型统计": {"序号": "int64", "作者编号": "int64", "点赞数": "int64", "评论数": "int64", "分享数": "int64", "BGM": "str", "时长": "float64", "发布日期": "str", "发布时间": "str", "类别": "str", "标题字数": "int64"}, "前5行示例": {"序号": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5}, "作者编号": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2}, "点赞数": {"0": 4093719, "1": 3263395, "2": 2962712, "3": 2953051, "4": 2821680}, "评论数": {"0": 1035, "1": 59098, "2": 52549, "3": 55461, "4": 52263}, "分享数": {"0": 160448, "1": 214594, "2": 109605, "3": 215838, "4": 125418}, "BGM": {"0": "作者创作的原声", "1": "作者创作的原声", "2": "作者创作的原声", "3": "作者创作的原声", "4": "作者创作的原声"}, "时长": {"0": 15.0, "1": 58.33, "2": 57.6, "3": 50.8, "4": 51.57}, "发布日期": {"0": "2019/5/6", "1": "2019/1/4", "2": "2019/2/11", "3": "2019/1/26", "4": "2019/1/29"}, "发布时间": {"0": "17:47:07", "1": "17:17:59", "2": "17:33:23", "3": "17:44:18", "4": "17:06:04"}, "类别": {"0": "美食", "1": "美食", "2": "美食", "3": "美食", "4": "美食"}, "标题字数": {"0": 44, "1": 11, "2": 12, "3": 12, "4": 13}}, "基本统计信息": {"序号": {"count": 6400.0, "mean": 3200.5, "std": 1847.665193336354, "min": 1.0, "25%": 1600.75, "50%": 3200.5, "75%": 4800.25, "max": 6400.0}, "作者编号": {"count": 6400.0, "mean": 1280.5575, "std": 806.8901968582244, "min": 1.0, "25%": 531.75, "50%": 1331.5, "75%": 1992.25, "max": 2612.0}, "点赞数": {"count": 6400.0, "mean": 651382.5003125, "std": 514325.35558265593, "min": 15165.0, "25%": 309374.25, "50%": 538962.5, "75%": 844416.25, "max": 4556768.0}, "评论数": {"count": 6400.0, "mean": 11701.84375, "std": 13348.544689948236, "min": 28.0, "25%": 3216.0, "50%": 7256.5, "75%": 14887.25, "max": 120245.0}, "分享数": {"count": 6400.0, "mean": 21954.7121875, "std": 34354.26363146099, "min": 3.0, "25%": 2586.5, "50%": 7796.5, "75%": 24420.25, "max": 347589.0}, "时长": {"count": 6400.0, "mean": 29.591785, "std": 17.540802322461424, "min": 4.4, "25%": 14.33, "50%": 24.785, "75%": 45.5, "max": 60.04}, "标题字数": {"count": 6400.0, "mean": 26.7140625, "std": 13.676461187735226, "min": 0.0, "25%": 16.0, "50%": 26.0, "75%": 37.0, "max": 72.0}}, "缺失值统计": {"序号": 0, "作者编号": 0, "点赞数": 0, "评论数": 0, "分享数": 0, "BGM": 1, "时长": 0, "发布日期": 0, "发布时间": 0, "类别": 0, "标题字数": 0}}}, "question": "视频的点赞数分布呈现出什么样的形态？"}
    '''

    result='''
    {
  "category": "连续型变量分布",
  "variable": {
    "data.pkl": ["点赞数"]
  },
  "role": {
    "data.pkl": ["NR"]
  },
  "answer": "首先，从数据集 data.pkl 中提取点赞数变量；其次，通过直方图或密度图可视化其分布形态，观察是否对称、偏态（左偏或右偏）、峰度（尖峰或平峰）以及异常值；同时计算基本统计量（如均值、中位数、标准差、四分位距）以量化集中趋势和离散程度；最后，结合图形和统计量总结分布特征（例如是否近似正态分布、是否存在长尾现象）。"
}
    '''

    answer={'category': '连续型变量分布', 'variable': {'data.pkl': ['点赞数']}, 'answer': '绘制点赞数的直方图。点赞数的分布呈现出右偏分布形态，显示出大多数视频的点赞数较低，只有少部分视频能够获得较高的点赞数，其中“人气之王”点赞数甚至高达400万。'}

    print(evaluate_0(question_description, result, answer))
