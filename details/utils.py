# encoding: utf-8

"""
处理数据的其他函数
"""
from . import config
import json
from pathlib import Path
from typing import List, Dict, Any

def parse_txt(file) -> List[Dict]:
    lines: List[str] = file.read().decode('utf-8').splitlines()
    # 创建数据
    data = [
        {
            config.TEXT: line.strip(),
            config.TAGS: [],
            config.LABELS: [],
            config.RELATIONS: []
        } for line in lines if line.strip()
    ]
    return data

def parse_json(file) -> List[Dict]:
    rawdata = file.read().decode('utf-8')
    parsed_data = json.loads(rawdata)
    # 验证输入数据的合法性
    assert isinstance(parsed_data, list), "数据格式错误，应该是一个列表"
    for item in parsed_data:
        assert isinstance(item, dict), "数据格式错误，列表中的每个元素应该是一个字典"
        assert all(key in item for key in [config.TEXT, config.TAGS, config.LABELS, config.RELATIONS]), "数据格式错误，缺少必要的字段"
    return parsed_data

def parse_file(file) -> List[Dict]:
    """根据文件后缀名解析数据

    Args:
        file: 文件流

    Raises:
        ValueError: 不支持的文件类型
    """
    suffix = Path(file.name).suffix.lower()
    if suffix == '.txt':
        return parse_txt(file)
    elif suffix == '.json':
        return parse_json(file)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

def check_labels_no_overlap(labels: List[Dict[str, Any]]) -> bool:
    """检查labels的起始、终止部分是否存在重叠
    
    Args: 
        labels: 表示label的字典序列

    Returns:
        bool: 对labels的起始、终止部分是否存在重叠的判定
    """
    if len(labels) <= 1:
        return True
    else:
        sorted_labels = sorted(labels, key=lambda x: x[config.START])
        for x in range(len(sorted_labels) - 1):
            current_end = sorted_labels[x][config.END]
            next_start = sorted_labels[x + 1][config.START]
            if current_end > next_start:
                return False
        return True