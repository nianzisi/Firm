import os
from pathlib import Path


def creat_env(path: str = r"D:\Seed\firm\agent\os.env"):
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Warning: {path} not found")
    key = []
    value = []
    with open(file_path, "r", encoding='utf-8') as f:
        for line in f:
            #  实例格式:  api_url = "https://api.deepseek.com/chat/completions" #123
            if line.startswith("#") or not line.strip():  # 跳过空行和注释行
                continue
            if "#" in line and not line.startswith("#"):
                line = line.split("#", 1)[0].strip()  # 实例格式:  api_url = "https://api.deepseek.com/chat/completions"
            if "=" not in line:
                raise ValueError("Warning: = not found")
            line = line.split("=", 1)
            _key: str = line[0]
            _value: str = line[1]
            while _key.startswith((" ", "'", '"')) or _value.startswith((" ", "'", '"'))\
                    or _key.endswith((" ", "'", '"')) or _value.endswith((" ", "'", '"')):
                _key = _key.strip("'\"").strip()
                _value = _value.strip("'\"").strip()
            key.append(_key)
            value.append(_value)

    if key and value:
        for _key, _value in zip(key, value):
            os.environ[_key] = _value
    return True, [key, value]
