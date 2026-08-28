import re
import json
from typing import Optional, Dict, Any

def extract_last_json_safe(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extract the last JSON object from text and parse it into a dictionary

    Args:
        text: text string containing JSON

    Returns:
        parsed dictionary, or None if no valid JSON found
    """
    if not text or not isinstance(text, str):
        return None
    
    # Try multiple extraction strategies
    # Strategy 2 (bracket matching) takes priority: correctly extracts the outer complete JSON object, avoiding mistakenly extracting nested inner objects
    strategies = [
        _extract_by_brace_matching,
        _extract_by_regex,
        _extract_by_find_last_brace
    ]
    
    for strategy in strategies:
        try:
            result = strategy(text)
            if result is not None:
                return result
        except Exception:
            continue
    
    return None

def _extract_by_regex(text: str) -> Optional[Dict]:
    """Strategy 1: Use regex"""
    # Match simple JSON objects
    pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    matches = re.findall(pattern, text)
    
    for json_str in reversed(matches):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            continue
    return None

def _extract_by_brace_matching(text: str) -> Optional[Dict]:
    """Strategy 2: Bracket matching method"""
    json_strings = []
    i = 0
    length = len(text)
    
    while i < length:
        if text[i] == '{':
            bracket_count = 1
            j = i + 1
            
            while j < length and bracket_count > 0:
                if text[j] == '{':
                    bracket_count += 1
                elif text[j] == '}':
                    bracket_count -= 1
                j += 1
            
            if bracket_count == 0:
                json_strings.append(text[i:j])
                i = j
            else:
                i += 1
        else:
            i += 1
    
    for json_str in reversed(json_strings):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            continue
    return None

def _extract_by_find_last_brace(text: str) -> Optional[Dict]:
    """Strategy 3: Find the last opening brace"""
    last_open = text.rfind('{')
    if last_open == -1:
        return None
    
    bracket_count = 1
    pos = last_open + 1
    
    while pos < len(text) and bracket_count > 0:
        if text[pos] == '{':
            bracket_count += 1
        elif text[pos] == '}':
            bracket_count -= 1
        pos += 1
    
    if bracket_count == 0:
        try:
            return json.loads(text[last_open:pos])
        except json.JSONDecodeError:
            pass
    
    return None

# Usage example
if __name__ == "__main__":
    test_text = """
    User: Hello
    System: {"response": "Hello, how can I help you?"}
    User: Query weather
    System: {
        "action": "weather_query",
        "params": {
            "city": "Beijing",
            "date": "2024-01-01"
        },
        "status": "success"
    }
    """

    result = extract_last_json_safe(test_text)
    if result:
        print("Successfully extracted the last JSON segment:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("No valid JSON segment found")