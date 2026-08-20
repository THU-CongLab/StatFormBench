import re
import json
from typing import Optional, Dict, Any

def extract_last_json_safe(text: str) -> Optional[Dict[str, Any]]:
    """
    安全地从文本中提取最后一个JSON对象并解析为字典
    
    参数:
        text: 包含JSON的文本字符串
    
    返回:
        解析后的字典，如果没有找到有效的JSON则返回None
    """
    if not text or not isinstance(text, str):
        return None
    
    # 尝试多种提取策略
    # 策略2（括号匹配）优先：能正确提取外层完整JSON对象，避免误提取嵌套内部对象
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
    """策略1：使用正则表达式"""
    # 匹配简单的JSON对象
    pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    matches = re.findall(pattern, text)
    
    for json_str in reversed(matches):
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            continue
    return None

def _extract_by_brace_matching(text: str) -> Optional[Dict]:
    """策略2：括号匹配法"""
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
    """策略3：查找最后一个左括号"""
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

# 使用示例
if __name__ == "__main__":
    test_text = """
    用户：你好
    系统：{"response": "你好，有什么可以帮助你的？"}
    用户：查询天气
    系统：{
        "action": "weather_query",
        "params": {
            "city": "北京",
            "date": "2024-01-01"
        },
        "status": "success"
    }
    """
    
    result = extract_last_json_safe(test_text)
    if result:
        print("成功提取最后一个JSON段落：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("未找到有效的JSON段落")