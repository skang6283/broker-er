import os 
import json

def save_json(result_json, file_path):
    with open(os.path.join(file_path), "w", encoding="utf-8",) as f:
        json.dump(result_json, f, ensure_ascii=False, indent=4, sort_keys=False)


def read_json(file_path):
    with open(file_path) as f:
        result_dict = json.load(f)

    return result_dict