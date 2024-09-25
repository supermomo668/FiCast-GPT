import json
import re
from typing import Any, Dict
from pathlib import Path
import warnings

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

def save_json_based_script(script_content, path: Path, option: str) -> None:
    if option == "json":
        with path.with_suffix(".json").open('w', encoding='utf-8') as f:
            json.dump(script_content, f, ensure_ascii=False, indent=4)
    elif option == "human":
        with path.open('w', encoding='utf-8') as f:
            for item in script_content['dialogues']:
                if isinstance(item, dict) and 'speaker' in item and 'dialogue' in item:
                    f.write(f"{item['speaker']}: {item['dialogue']}\n")
                else:
                    warnings.warn(f"Invalid script item: {item}")

def save_raw_based_script(script_content, path: Path, option: str) -> None:
    if option == "text":
        with path.open('w', encoding='utf-8') as f:
            for item in script_content:
                f.write(item['content'] + '\n')
    elif option == "html":
        with path.with_suffix(".html").open('w', encoding='utf-8') as f:
            f.write("<html><body>\n")
            for item in script_content:
                f.write(f"<p>{item['content']}</p>\n")
            f.write("</body></html>")