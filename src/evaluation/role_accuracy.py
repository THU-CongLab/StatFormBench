def dict_to_list(data):
    return [key + value for key, values in data.items() for value in values]

def calculate_role_accuracy(answer, result):
    """
    Calculate the proportion of correct role judgments for answer["variable"] variables (answer["role"]) in result

    Args:
        answer (dict): dict containing correct answers, includes role field
        result (dict): dict of model prediction results, includes role field

    Returns:
        float: role accuracy, range 0-1
    """
    # Check if both answer and result contain role field
    if "role" not in answer or "role" not in result:
        return 0.0

    answer_role = answer.get("role", {})
    result_role = result.get("role", {})

    # Case 1: if both answer["role"] and result["role"] are empty dicts, consider all correct
    if not answer_role and not result_role:
        return 1.0

    # Case 2: if result["role"] is not empty but answer["role"] is empty, consider all incorrect
    if result_role and not answer_role:
        return 0.0

    # Case 3: calculate accuracy normally
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

    # Calculate accuracy
    if total_variables == 0:
        return 1.0
    else:
        return correct_roles / total_variables


def test_role_accuracy():
    """
    Test role accuracy calculation function
    """
    # Test case 1: both empty dicts
    answer1 = {"role": {}, "variable": {}}
    result1 = {"role": {}, "variable": {}}
    print(f"Test case 1 (both empty dicts): {calculate_role_accuracy(answer1, result1)}")

    # Test case 2: result not empty but answer empty
    answer2 = {"role": {}, "variable": {"LLM.pkl": ["Text", "Label"]}}
    result2 = {"role": {"LLM.pkl": ["independent", "dependent"]}, "variable": {"LLM.pkl": ["Text", "Label"]}}
    print(f"Test case 2 (result not empty but answer empty): {calculate_role_accuracy(answer2, result2)}")

    # Test case 3: all correct
    answer3 = {
        "role": {"LLM.pkl": ["independent", "dependent"],"LLM2.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"],"LLM2.pkl": ["A", "B"]}
    }
    result3 = {
        "role": {"LLM.pkl": ["independent", "dependent"],"LLM2.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"],"LLM2.pkl": ["A", "B"]}
    }
    print(f"Test case 3 (all correct): {calculate_role_accuracy(answer3, result3)}")

    # Test case 4: partially correct
    answer4 = {
        "role": {"LLM.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    result4 = {
        "role": {"LLM.pkl": ["independent", "independent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    print(f"Test case 4 (partially correct): {calculate_role_accuracy(answer4, result4)}")

    # Test case 5: all wrong
    answer5 = {
        "role": {"LLM.pkl": ["independent", "dependent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    result5 = {
        "role": {"LLM.pkl": ["dependent", "independent"]},
        "variable": {"LLM.pkl": ["Text", "Label"]}
    }
    print(f"Test case 5 (all wrong): {calculate_role_accuracy(answer5, result5)}")


if __name__ == "__main__":
    test_role_accuracy()