# encoding: utf-8

"""
处理数据的其他函数
"""
from . import config
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import deque

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

def remove_relations_by_object(relations: List[Dict[str, Any]], 
                               object_type: str, 
                               object_id: int) -> List[Dict[str, Any]]:
    """删除与指定对象关联的所有关系，使用图搜索方法级联删除相关关系
    
    Args:
        relations: 关系列表
        object_type: 要删除的对象类型 ('label' 或 'relation')
        object_id: 要删除的对象ID
    
    Returns:
        List[Dict[str, Any]]: 过滤后的关系列表
    """
    
    # 确保object_id是整数类型
    try:
        object_id = int(object_id)
    except (ValueError, TypeError):
        return relations  # 如果转换失败，返回原始关系列表
    
    # 构建对象到关系的映射
    object_to_relations = {}
    relation_id_to_relation = {}
    
    for relation in relations:
        rel_id = relation.get('id')
        if rel_id is not None:
            try:
                rel_id = int(rel_id)  # 确保关系ID也是整数
            except (ValueError, TypeError):
                continue  # 跳过无效的关系ID
                
            relation_id_to_relation[rel_id] = relation
            
            # 记录起始对象关联的关系
            start_obj = relation.get('start', {})
            start_obj_id = start_obj.get('id')
            if start_obj_id is not None:
                try:
                    start_obj_id = int(start_obj_id)
                    start_key = (start_obj.get('object_type'), start_obj_id)
                    if start_key not in object_to_relations:
                        object_to_relations[start_key] = set()
                    object_to_relations[start_key].add(rel_id)
                except (ValueError, TypeError):
                    pass  # 跳过无效的对象ID
            
            # 记录结束对象关联的关系
            end_obj = relation.get('end', {})
            end_obj_id = end_obj.get('id')
            if end_obj_id is not None:
                try:
                    end_obj_id = int(end_obj_id)
                    end_key = (end_obj.get('object_type'), end_obj_id)
                    if end_key not in object_to_relations:
                        object_to_relations[end_key] = set()
                    object_to_relations[end_key].add(rel_id)
                except (ValueError, TypeError):
                    pass  # 跳过无效的对象ID
    
    # 使用BFS查找所有需要删除的关系
    to_delete = set()  # 存储需要删除的关系ID
    queue = deque()
    
    # 初始化队列：找到与指定对象直接关联的关系
    initial_key = (object_type, object_id)
    if initial_key in object_to_relations:
        for rel_id in object_to_relations[initial_key]:
            queue.append(rel_id)
            to_delete.add(rel_id)
    
    # BFS遍历，查找级联删除的关系
    while queue:
        current_rel_id = queue.popleft()
        
        # 检查与当前关系关联的其他关系
        relation_key = ('relation', current_rel_id)
        if relation_key in object_to_relations:
            for rel_id in object_to_relations[relation_key]:
                if rel_id not in to_delete:
                    queue.append(rel_id)
                    to_delete.add(rel_id)
    
    # 过滤掉需要删除的关系
    filtered_relations = []
    for relation in relations:
        rel_id = relation.get('id')
        if rel_id is None:
            filtered_relations.append(relation)
        else:
            try:
                rel_id_int = int(rel_id)
                if rel_id_int not in to_delete:
                    filtered_relations.append(relation)
            except (ValueError, TypeError):
                # 如果ID无法转换为整数，保留该关系
                filtered_relations.append(relation)
    
    return filtered_relations