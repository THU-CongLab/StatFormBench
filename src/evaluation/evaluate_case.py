import os
from json_utils import extract_last_json_safe
from variable_metrics import jaccard_coefficient, calculate_ratio_set
from compare_methods import compare_methods0, compare_methods1
from llm_evaluator import evaluate_statistical_model
from role_accuracy import calculate_role_accuracy

example_model_score={
  "score": 0,
  "dimension_scores": {
    "method_appropriateness": 0,
    "process_logic": 0,
    "comparison_with_reference": 0
  },
  "comment": "None"
}

def dict_to_set(data):
    return {key + value for key, values in data.items() for value in values}

def dict_to_list(data):
    return [key + value for key, values in data.items() for value in values]

def dict_structure_equal(dict1, dict2):
    """
    Check if two dictionaries have exactly the same structure
    """
    try:
        # Check if keys are exactly the same
        if dict1.keys() != dict2.keys():
            return False

        # Check if each key's value is a list and has the same length
        for key in dict1:
            val1, val2 = dict1[key], dict2[key]

            # Check if both are lists
            if not isinstance(val1, list) or not isinstance(val2, list):
                return False

            # Check list length
            if len(val1) != len(val2):
                return False

        return True

    except (AttributeError, TypeError):
        # Handle case where input is not a dictionary
        return False

def evaluate_0(question_description, result, answer):
    #answer is dict type
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
    {"background": "The popularity of short videos has prompted many content creators and brands to seek ways to improve video exposure and engagement, particularly likes. This task aims to explore factors affecting short video likes, helping content creators optimize their videos for better user feedback and engagement.", "data_description_1": "The dataset is sourced from a short video platform, containing 6400 short video records with 11 variables, including: id (unique identifier of the video), author_id (identifier of the video creator), likes (number of likes received by the video), comments (number of comments on the video), shares (number of times the video was shared), BGM (background music), duration (video duration), publish_date (date the video was published), publish_time (specific time the video was published), category (content category of the video), title_word_count (word count of the video title).", "data_description_2": {"data.pkl": {"data_type": "DataFrame", "data_shape": "6400 rows x 11 columns", "variable_names": ["id", "author_id", "likes", "comments", "shares", "BGM", "duration", "publish_date", "publish_time", "category", "title_word_count"], "data_type_statistics": {"id": "int64", "author_id": "int64", "likes": "int64", "comments": "int64", "shares": "int64", "BGM": "str", "duration": "float64", "publish_date": "str", "publish_time": "str", "category": "str", "title_word_count": "int64"}, "first_5_rows_example": {"id": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5}, "author_id": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2}, "likes": {"0": 4093719, "1": 3263395, "2": 2962712, "3": 2953051, "4": 2821680}, "comments": {"0": 1035, "1": 59098, "2": 52549, "3": 55461, "4": 52263}, "shares": {"0": 160448, "1": 214594, "2": 109605, "3": 215838, "4": 125418}, "BGM": {"0": "original audio by author", "1": "original audio by author", "2": "original audio by author", "3": "original audio by author", "4": "original audio by author"}, "duration": {"0": 15.0, "1": 58.33, "2": 57.6, "3": 50.8, "4": 51.57}, "publish_date": {"0": "2019/5/6", "1": "2019/1/4", "2": "2019/2/11", "3": "2019/1/26", "4": "2019/1/29"}, "publish_time": {"0": "17:47:07", "1": "17:17:59", "2": "17:33:23", "3": "17:44:18", "4": "17:06:04"}, "category": {"0": "food", "1": "food", "2": "food", "3": "food", "4": "food"}, "title_word_count": {"0": 44, "1": 11, "2": 12, "3": 12, "4": 13}}, "basic_statistics": {"id": {"count": 6400.0, "mean": 3200.5, "std": 1847.665193336354, "min": 1.0, "25%": 1600.75, "50%": 3200.5, "75%": 4800.25, "max": 6400.0}, "author_id": {"count": 6400.0, "mean": 1280.5575, "std": 806.8901968582244, "min": 1.0, "25%": 531.75, "50%": 1331.5, "75%": 1992.25, "max": 2612.0}, "likes": {"count": 6400.0, "mean": 651382.5003125, "std": 514325.35558265593, "min": 15165.0, "25%": 309374.25, "50%": 538962.5, "75%": 844416.25, "max": 4556768.0}, "comments": {"count": 6400.0, "mean": 11701.84375, "std": 13348.544689948236, "min": 28.0, "25%": 3216.0, "50%": 7256.5, "75%": 14887.25, "max": 120245.0}, "shares": {"count": 6400.0, "mean": 21954.7121875, "std": 34354.26363146099, "min": 3.0, "25%": 2586.5, "50%": 7796.5, "75%": 24420.25, "max": 347589.0}, "duration": {"count": 6400.0, "mean": 29.591785, "std": 17.540802322461424, "min": 4.4, "25%": 14.33, "50%": 24.785, "75%": 45.5, "max": 60.04}, "title_word_count": {"count": 6400.0, "mean": 26.7140625, "std": 13.676461187735226, "min": 0.0, "25%": 16.0, "50%": 26.0, "75%": 37.0, "max": 72.0}}, "missing_value_statistics": {"id": 0, "author_id": 0, "likes": 0, "comments": 0, "shares": 0, "BGM": 1, "duration": 0, "publish_date": 0, "publish_time": 0, "category": 0, "title_word_count": 0}}}, "question": "What is the distribution shape of video likes?"}
    '''

    result='''
    {
  "category": "Continuous variable distribution",
  "variable": {
    "data.pkl": ["likes"]
  },
  "role": {
    "data.pkl": ["NR"]
  },
  "answer": "First, extract the likes variable from the dataset data.pkl; second, visualize its distribution shape through histograms or density plots, observing symmetry, skewness (left or right), kurtosis (peaked or flat), and outliers; simultaneously calculate basic statistics (such as mean, median, standard deviation, interquartile range) to quantify central tendency and dispersion; finally, combine the graphs and statistics to summarize the distribution characteristics (e.g., whether it approximates a normal distribution, whether there is a long-tail phenomenon)."
}
    '''

    answer={'category': 'Continuous variable distribution', 'variable': {'data.pkl': ['likes']}, 'answer': 'Draw a histogram of likes. The distribution of likes shows a right-skewed distribution, indicating that most videos have a low number of likes, while only a small portion of videos receive high numbers of likes, with the most popular video reaching 4 million likes.'}

    print(evaluate_0(question_description, result, answer))
