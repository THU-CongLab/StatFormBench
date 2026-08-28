import openai
import json
import os
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

#from prompts.prompts import prompt_evaluate0
from config.api_config import api_key, base_url
from json_utils import extract_last_json_safe

def check_dictionary_structure(data):
    """
    Check if dictionary matches the specified scoring structure

    Args:
        data: dictionary to check

    Returns:
        bool: True if structure is correct, False otherwise
    """
    # Check if it's a dictionary
    if not isinstance(data, dict):
        return False

    # Check if required keys exist
    required_keys = {"score", "dimension_scores", "comment"}
    if not all(key in data for key in required_keys):
        return False

    # Check score type and range
    if not isinstance(data["score"], (int, float)):
        return False

    # Check if dimension_scores is a dictionary
    if not isinstance(data["dimension_scores"], dict):
        return False

    # Check required keys in dimension_scores
    required_dimensions = {"method_appropriateness", "process_logic", "comparison_with_reference"}
    dimension_scores = data["dimension_scores"]

    if not all(dim in dimension_scores for dim in required_dimensions):
        return False

    # Check dimension score types
    for dim in required_dimensions:
        if not isinstance(dimension_scores[dim], (int, float)):
            return False

    # Check comment type
    if not isinstance(data["comment"], str):
        return False

    return True


def evaluate_statistical_model(question_description, candidate_model, reference_model, model_name="gpt-5.2"):
    """
    Call LLM to evaluate statistical model abstraction results

    Args:
        question_description (dict): Question description, containing background, data_description_1, question, etc.
        reference_model (dict): Reference statistical model, containing method, variable, answer
        candidate_model (dict): Statistical model to evaluate, containing method, variable, answer
        model_name (str): Name of the model to use

    Returns:
        dict: Evaluation result, containing score, dimension_scores, and comment
    """
    # Build complete prompt
    input_data = {
        "Question description": question_description,
        "Reference statistical model": reference_model,
        "Statistical model to evaluate": candidate_model
    }

    prompt = f"{prompt_evaluate0}\n\nInput information:\n{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\nPlease output the review report in the required JSON format:"

    # Call OpenAI API
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an experienced statistical methodology expert and reviewer"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1000
    )

    # Extract model output
    output = response.choices[0].message.content.strip()

    # Use extract_last_json_safe to extract complete JSON
    result = extract_last_json_safe(output)
    
    if result is None or check_dictionary_structure(result)==False:
        return "unsuccessful"
    else:
        return result


def batch_evaluate(input_file, output_file, model_name="gpt-5"):
    """
    Batch evaluate multiple statistical models

    Args:
        input_file (str): Input file path, containing multiple evaluation cases
        output_file (str): Output file path, saving evaluation results
        model_name (str): Name of the model to use
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    results = []

    # Evaluate each case
    for i, case in enumerate(cases):
        print(f"Evaluating case {i+1}/{len(cases)}...")

        try:
            question_description = case['question_description']
            reference_model = case['reference_model']
            candidate_model = case['candidate_model']

            # Call evaluation function
            result = evaluate_statistical_model(
                question_description,
                reference_model,
                candidate_model,
                model_name
            )

            # Add case information
            result['case_id'] = case.get('case_id', i+1)
            result['input'] = case

            results.append(result)

            # Add delay to avoid API rate limits
            import time
            time.sleep(1)

        except Exception as e:
            print(f"Evaluating case {i+1} failed: {e}")
            # Add error record
            error_result = {
                'case_id': case.get('case_id', i+1),
                'error': str(e),
                'input': case
            }
            results.append(error_result)

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Evaluation complete! Results saved to {output_file}")
    print(f"Total evaluated {len(results)} cases")

    return results


if __name__ == "__main__":
    # Test example
    test_question_description = {
        "background": "The Global Gender Gap Report (GGGR) is a report aimed at measuring progress in gender equality across countries.",
        "data_description_1": "The data consists of two parts: (1) comprehensive scores and sub-scores provided by GGGR; (2) economic development indicators provided by the World Bank.",
        "question": "Which factors have a significant impact on the gender equality score?"
    }

    test_reference_model = {
        "category": "Regression coefficient significance and direction interpretation",
        "variable": {"gggr_data.pkl": ["gender_equality_score", "gdp_per_capita", "education_index"]},
        "answer": "Use multiple linear regression model with gender equality score as dependent variable and GDP per capita and education index as independent variables to analyze the direction and significance of each factor's impact on gender equality."
    }

    test_candidate_model = {
        "category": "Continuous value prediction",
        "variable": {"gggr_data.pkl": ["gender_equality_score", "gdp_per_capita", "education_index"]},
        "answer": "Use multiple linear regression model with gender equality score as dependent variable and GDP per capita and education index as independent variables to predict gender equality score and analyze the impact of each factor."
    }

    print("Testing evaluation function...")
    result = evaluate_statistical_model(
        test_question_description,
        test_reference_model,
        test_candidate_model
    )

    print("Evaluation result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))