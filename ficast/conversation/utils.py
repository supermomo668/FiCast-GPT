import json
import re
from typing import Any, Dict

def clean_json_string(input_string):
    # Remove markdown code block delimiters and any trailing new lines
    cleaned_str = re.sub(r'```json\n|\n```|\)', '', input_string).strip()
    return cleaned_str

def extract_json_code_block(s: str) -> Dict[str, Any]:
    # Define a regex pattern to match JSON code blocks
    pattern = r'```json\s*([\s\S]*?)\s*```'
    
    # Find all JSON code blocks
    match = re.search(pattern, s)
    if not match:
        raise ValueError("No valid JSON code blocks found.")
    # Convert each JSON string to a dictionary
    json_str = clean_json_string(match[0])
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")