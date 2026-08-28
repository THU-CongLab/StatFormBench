import csv
import os


def load_method_hierarchy():
    """
    Load method_hierarchy.csv file, return mapping from method to hierarchy1
    """
    method_hierarchy = {}
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'method_hierarchy.csv')

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if row is valid
            if 'hierarchy2' in row and 'hierarchy1' in row:
                method = row['hierarchy2'].strip() if row['hierarchy2'] else ''
                hierarchy = row['hierarchy1'].strip() if row['hierarchy1'] else ''
                if method and hierarchy:
                    method_hierarchy[method] = hierarchy

    return method_hierarchy



def compare_methods0(a, b):
    """
    Strict match: return 1 if and only if a and b are exactly equal, otherwise return 0

    Args:
        a (str): first method string
        b (str): second method string

    Returns:
        int: 1 means identical, 0 means different
    """
    return 1 if a == b else 0



def compare_methods1(a, b):
    """
    Compare two method strings a and b, return corresponding value based on rules

    Args:
        a (str): first method string
        b (str): second method string

    Returns:
        float: Return 0, 0.5, or 1 based on rules
    """
    # Load method-to-hierarchy mapping
    method_hierarchy = load_method_hierarchy()

    # Check if a and b exist in hierarchy2
    a_exists = a in method_hierarchy
    b_exists = b in method_hierarchy

    # Rule 1: if a or b does not exist, return 0
    if not a_exists or not b_exists:
        return 0

    # Rule 2: if hierarchy1 of a and b are the same
    if method_hierarchy[a] == method_hierarchy[b]:
        return 1

    # Return 0 for other cases
    return 0


def batch_compare(input_pairs, output_file=None):
    """
    Batch compare method pairs

    Args:
        input_pairs (list): list of method pairs, each element is a (a, b) tuple
        output_file (str, optional): output file path

    Returns:
        list: list of comparison results
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
        print(f"Batch comparison results saved to {output_file}")

    return results


if __name__ == "__main__":
    # Test example
    test_cases = [
        ("Discrete variable distribution", "Discrete variable distribution"),  # should return 1
        ("Discrete variable distribution", "Continuous variable distribution"),  # should return 0.5 (both belong to data visualization)
        ("Discrete variable distribution", "Regression coefficient significance and direction interpretation"),  # should return 0 (different hierarchy)
        ("Discrete variable distribution", "Non-existent method"),  # should return 0 (b does not exist)
        ("Non-existent method", "Discrete variable distribution"),  # should return 0 (a does not exist)
        ("Non-existent method1", "Non-existent method2"),  # should return 0 (neither exists)
    ]

    print("Testing comparison methods:")
    for a, b in test_cases:
        score = compare_methods1(a, b)
        print(f"{a} vs {b} = {score}")

    # Testing batch comparison
    print("\nTesting batch comparison:")
    batch_results = batch_compare(test_cases, 'compare_results.csv')
    for result in batch_results:
        print(result)