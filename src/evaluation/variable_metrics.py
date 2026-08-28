import pickle
import pandas as pd
import numpy as np
import random
import re
import json

def jaccard_coefficient(A, B):
    """
    Calculate the Jaccard coefficient of sets A and B.

    Args:
        A (set): set A
        B (set): set B

    Returns:
        float: Jaccard coefficient
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
    Calculate the proportion of elements in set A that exist in set B (using set operations)

    Args:
        A: iterable object, such as list, tuple, set, etc.
        B: iterable object, such as list, tuple, set, etc.

    Returns:
        float: existence ratio (between 0.0 and 1.0)
    """
    # Convert to sets for efficient lookup
    set_A = set(A)
    set_B = set(B)

    # Count elements in A that also exist in B
    common_count = len(set_A & set_B)

    # Calculate the ratio
    if len(set_A) == 0:
        return 0.0  # handle empty set case

    return common_count / len(set_A)