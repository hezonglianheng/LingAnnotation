from django.shortcuts import render

# Create your views here.
from . import utils, config
from listing.models import TaskRecord
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from pathlib import Path
import json
import zipfile
import os
from typing import Dict, Any, List

def task_detail(request, task_id):
    # Fetch the task record from the database using the task_id
    task_record = TaskRecord.objects.get(task_id=task_id)
    task_dirpath = task_record.task_dirpath
    # print(task_dirpath)
    data_filepath = Path(task_dirpath) / 'data.json'
    with data_filepath.open("r", encoding='utf-8') as f:
        data = json.load(f)
    
    # print(data[0])
    # Render the template with the task record
    return render(request, 'details/index.html', {'task': task_record, "corpus_items": data})

@ensure_csrf_cookie
def upload_data(request, task_id):
    if request.method == 'POST':
        try:
            # Handle the file upload
            task_record = TaskRecord.objects.get(task_id=task_id)
            task_dir = task_record.task_dirpath
        
            # Assuming the uploaded file is in request.FILES['file']
            uploaded_file = request.FILES['file']
        
            # parse the file based on its extension
            parsed_data = utils.parse_file(uploaded_file)

            # Save the parsed data to a file in the task directory
            file_path = Path(task_dir) / 'data.json'
            with file_path.open("r", encoding='utf-8') as f:
                existing_data: list[dict] = json.load(f)
            max_id = 0
            for item in existing_data:
                if item[config.ID] > max_id:
                    max_id = item[config.ID]
            for i, item in enumerate(parsed_data, start=max_id):
                item[config.ID] = i + 1
            existing_data.extend(parsed_data)
            with file_path.open("w", encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)

            return JsonResponse({'status': 'success'})  # Return a success response after processing the upload
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"文件上传出现错误: {str(e)}"})
    return JsonResponse({'status': 'error', 'message': '只接受POST请求'})

@ensure_csrf_cookie
def download_data(request, task_id):
    try:
        # 获取任务记录
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_dir = task_record.task_dirpath
        task_name = task_record.task_name.replace(" ", "_")  # 替换空格，用于文件名
    
        # 创建zip文件路径
        zip_file_path = Path(task_dir) / 'data.zip'
        
        # 创建zip文件
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(task_dir):
                for file in files:
                    # 跳过zip文件本身
                    if file == 'data.zip':
                        continue
                    file_path = Path(root) / file
                    # 将文件添加到zip中，保留相对路径
                    zipf.write(file_path, file_path.relative_to(task_dir))
        
        # 确认文件已生成
        if not os.path.exists(zip_file_path):
            return JsonResponse({'status': 'error', 'message': '压缩文件生成失败'})
        
        # 设置文件名
        filename = f"task_{task_id}_{task_name}.zip"
        
        # 打开文件并返回
        with open(zip_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except TaskRecord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'找不到任务ID: {task_id}'})
    except Exception as e:
        # 详细记录异常信息
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({'status': 'error', 'message': f"文件下载失败: {str(e)}", 'details': error_details})

@ensure_csrf_cookie
def update_task_info(request, task_id):
    # Fetch the task record from the database using the task_id
    task_record = TaskRecord.objects.get(task_id=task_id)
    task_name = task_record.task_name
    task_description = task_record.task_description
    return render(request, 'details/update_info.html', {
        'task_id': task_id,
        'task_name': task_name,
        'task_description': task_description,
    })

@ensure_csrf_cookie
def delete_task_item(request):
    if request.method == 'POST':
        try:
            # 从请求体中获取JSON数据
            data = json.loads(request.body)
            task_id = data.get('task_id')
            item_id = data.get('item_id')
            # print(task_id, item_id)
            
            # 检查task_id和item_id是否为整数
            if not isinstance(task_id, int) or not isinstance(item_id, int):
                return JsonResponse({'status': 'error', 'message': '无效的任务ID或条目ID'})
            
            # 查询任务记录
            task_record = TaskRecord.objects.get(task_id=task_id)
            task_dirpath = task_record.task_dirpath
            
            # 删除条目
            file_path = Path(task_dirpath) / 'data.json'
            with file_path.open("r", encoding='utf-8') as f:
                data = json.load(f)
            
            # 删除指定ID的条目
            data = [item for item in data if item[config.ID] != item_id]
            
            # 保存更新后的数据
            with file_path.open("w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"删除条目失败: {str(e)}"})
    return JsonResponse({'status': 'error', 'message': '只接受POST请求'})

@ensure_csrf_cookie
def show_item(request, task_id, item_id):
    try:
        # 获取任务记录
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_dirpath = task_record.task_dirpath
        
        # 读取数据文件
        file_path = Path(task_dirpath) / 'data.json'
        # print(file_path)
        with file_path.open("r", encoding='utf-8') as f:
            data = json.load(f)
        
        # print(data[0])
        # 查找指定ID的条目
        item: Dict[str, Any] = next((item for item in data if item[config.ID] == item_id), None)
        
        if not item:
            return JsonResponse({'status': 'error', 'message': '未找到指定条目'})
        
        # TODO: 设计显示逻辑
        # 处理label的显示
        sorted_labels = sorted(item[config.LABELS], key=lambda x: (x[config.START], x[config.END]))
        if not utils.check_labels_no_overlap(sorted_labels):
            return JsonResponse({'status': 'error', 'message': '标签存在重叠，无法显示'})

        # 根据标签的起始和终止位置切分文本，用于后续显示
        text = item[config.TEXT]
        segments = []
        last_end = 0
        for label in sorted_labels:
            start = label[config.START]
            end = label[config.END]
            segments.append({'text': text[last_end:start], 'label': None, 'start': last_end, 'end': start})
            segments.append({'text': text[start:end], 'label': label, 'start': start, 'end': end})
            last_end = end
        if last_end < len(text):
            segments.append({'text': text[last_end:], 'label': None, 'start': last_end, 'end': len(text)})

        # 读取tag, label, relation信息
        def read_json_file(filename):
            file_path = Path(task_dirpath) / filename
            if not file_path.exists():
                return []
            with file_path.open('r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return data
                except Exception:
                    return []

        tags = read_json_file('tag.json')
        labels = read_json_file('label.json')
        relations = read_json_file('relation.json')

        # 构建类型到颜色的映射（label.json 里每个 label 需有 name 和 color 字段）
        label_type2color = {l['name']: l.get('color', '#3498db') for l in labels}

        # 根据标签的起始和终止位置切分文本，并为每个有 label 的 segment 加入 color
        text = item[config.TEXT]
        segments = []
        last_end = 0
        for label in sorted_labels:
            start = label[config.START]
            end = label[config.END]
            color = label_type2color.get(label['type'], '#3498db')
            if last_end < start:
                segments.append({'text': text[last_end:start], 'label': None, 'start': last_end, 'end': start})
            segments.append({'text': text[start:end], 'label': label, 'start': start, 'end': end, 'color': color})
            last_end = end
        if last_end < len(text):
            segments.append({'text': text[last_end:], 'label': None, 'start': last_end, 'end': len(text)})
        # 传递原始文本和segments（含原始索引、颜色）到前端
        return render(request, 'details/showitem.html', {
            'task': task_record,
            'item': item,
            'segments': segments,
            'tags': tags,
            'labels': labels,
            'relations': relations,
            'original_text': text
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"显示条目失败: {str(e)}"})

@ensure_csrf_cookie
def label_create_page(request, task_id):
    return render(request, 'details/label_create.html', {'task_id': task_id})

@ensure_csrf_cookie
def label_creation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            color = data.get('color')
            label_type = data.get('type')
            task_id = data.get('task_id')

            # 获取任务记录
            task_record = TaskRecord.objects.get(task_id=task_id)
            task_dirpath = task_record.task_dirpath

            if label_type == "tag":
                # 读取数据文件
                file_path = Path(task_dirpath) / 'tag.json'
            elif label_type == "label":
                file_path = Path(task_dirpath) / 'label.json'
            elif label_type == "relation":
                file_path = Path(task_dirpath) / 'relation.json'
            else:
                return JsonResponse({'status': 'error', 'message': f"未知的类型: {label_type}"})

            with file_path.open("r", encoding='utf-8') as f:
                existing_data: List[Dict[str, Any]] = json.load(f)

            # 检查是否存在重名
            if any(item['name'] == name for item in existing_data):
                return JsonResponse({'status': 'error', 'message': f"标签名已存在: {name}"})
            
            # 创建新标签
            new_label = {
                'name': name,
                'color': color,
                'type': label_type
            }

            existing_data.append(new_label)

            with file_path.open("w", encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)

            return JsonResponse({'status': 'success', 'message': '标签创建成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"请求数据解析失败: {str(e)}"})
    else:
        return JsonResponse({'status': 'error', 'message': '只接受POST请求'})

@ensure_csrf_cookie
def get_labels(request):
    """
    获取指定任务下所有的tag、label、relation信息，返回json
    GET参数: task_id
    返回: {tags: [...], labels: [...], relations: [...]}
    """
    try:
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({'status': 'error', 'message': '缺少task_id'})
        # 获取任务记录
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_dirpath = task_record.task_dirpath
        # 读取tag、label、relation文件
        def read_json_file(filename):
            file_path = Path(task_dirpath) / filename
            if not file_path.exists():
                return []
            with file_path.open('r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # 补充id字段（前端需要）
                    for idx, item in enumerate(data):
                        if 'id' not in item:
                            item['id'] = idx + 1
                    return data
                except Exception:
                    return []
        tags = read_json_file('tag.json')
        labels = read_json_file('label.json')
        relations = read_json_file('relation.json')
        return JsonResponse({'tags': tags, 'labels': labels, 'relations': relations, 'status': 'success'})
    except TaskRecord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '找不到任务ID'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取标签失败: {str(e)}'})

@ensure_csrf_cookie
def delete_labels(request):
    """
    删除指定类型的标签/文本/关系，并同步删除所有数据中引用该标签的内容。
    POST参数: {type: tag/label/relation, ids: [id1, id2, ...], task_id: xxx}
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只接受POST请求'})
    try:
        data = json.loads(request.body)
        label_type = data.get('type')
        ids = data.get('ids')
        task_id = data.get('task_id') or request.GET.get('task_id')
        if not label_type or not ids or not task_id:
            return JsonResponse({'status': 'error', 'message': '缺少必要参数'})
        # 获取任务记录
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_dirpath = task_record.task_dirpath
        # 文件名映射
        type2file = {'tag': 'tag.json', 'label': 'label.json', 'relation': 'relation.json'}
        if label_type not in type2file:
            return JsonResponse({'status': 'error', 'message': '类型错误'})
        file_path = Path(task_dirpath) / type2file[label_type]
        if not file_path.exists():
            return JsonResponse({'status': 'error', 'message': '标签文件不存在'})
        # 读取原始标签列表
        with file_path.open('r', encoding='utf-8') as f:
            label_list = json.load(f)
        # 找到要删除的标签名
        del_names = []
        for idx, item in enumerate(label_list):
            if str(item.get('id', idx+1)) in ids or str(idx+1) in ids:
                del_names.append(item['name'])
        # 删除标签
        new_label_list = [item for idx, item in enumerate(label_list) if not (str(item.get('id', idx+1)) in ids or str(idx+1) in ids)]
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(new_label_list, f, ensure_ascii=False, indent=4)

        # 级联删除数据中引用该标签的内容
        # 只对label和tag类型做数据清理，relation可选
        if label_type in ('tag', 'label'):
            data_file = Path(task_dirpath) / 'data.json'
            if data_file.exists():
                with data_file.open('r', encoding='utf-8') as f:
                    data_items = json.load(f)
                changed = False
                for item in data_items:
                    # 标签信息一般在item['labels']或item['tags']，需根据实际结构调整
                    # 这里假设所有标签都在item['labels']，且有'type'字段
                    if 'labels' in item and isinstance(item['labels'], list):
                        before = len(item['labels'])
                        item['labels'] = [lab for lab in item['labels'] if lab.get('type') not in del_names]
                        if len(item['labels']) != before:
                            changed = True
                    # 兼容tag字段
                    if 'tags' in item and isinstance(item['tags'], list):
                        before = len(item['tags'])
                        item['tags'] = [lab for lab in item['tags'] if lab.get('type') not in del_names]
                        if len(item['tags']) != before:
                            changed = True
                if changed:
                    with data_file.open('w', encoding='utf-8') as f:
                        json.dump(data_items, f, ensure_ascii=False, indent=4)
        # relation类型如需级联删除可在此补充
        return JsonResponse({'status': 'success', 'message': '删除成功'})
    except TaskRecord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '找不到任务ID'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'删除失败: {str(e)}'})

@csrf_exempt
def add_label(request, task_id, item_id):
    """
    处理前端选中一段文本后点击标注信息的请求，
    将标注信息添加到对应的data.json条目和label.json/tag.json/relation.json中。
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只接受POST请求'})
    try:
        data = json.loads(request.body)
        label_type = data.get('type')  # 'label'/'tag'/'relation'
        name = data.get('name')
        color = data.get('color')
        start = data.get('start')
        end = data.get('end')
        # 获取任务和条目
        task_record = TaskRecord.objects.get(task_id=task_id)
        task_dirpath = task_record.task_dirpath
        data_file = Path(task_dirpath) / 'data.json'
        with data_file.open('r', encoding='utf-8') as f:
            items = json.load(f)
        # 找到对应item
        item = next((item for item in items if item[config.ID] == item_id), None)
        if not item:
            return JsonResponse({'status': 'error', 'message': '未找到指定条目'})
        # 构造新label对象
        new_label = {
            'type': name,
            # 'color': color, # 不需要传递color字段
            'start': start,
            'end': end
        }
        # 添加到item的labels/tag/relation字段
        if label_type == 'label':
            if config.LABELS not in item:
                item[config.LABELS] = []
            # Assign an ID to the new label
            label_id = 0 if not item[config.LABELS] else max(lab.get('id', 0) for lab in item[config.LABELS]) + 1
            new_label['id'] = label_id
            item[config.LABELS].append(new_label)
        elif label_type == 'tag':
            if 'tags' not in item:
                item[config.TAGS] = []
            # Assign an ID to the new tag
            tag_id = 0 if not item[config.TAGS] else max(tag.get('id', 0) for tag in item[config.TAGS]) + 1
            new_label['id'] = tag_id
            item[config.TAGS].append(new_label)
        elif label_type == 'relation':
            if 'relations' not in item:
                item[config.RELATIONS] = []
            # Assign an ID to the new relation
            relation_id = 0 if not item[config.RELATIONS] else max(rel.get('id', 0) for rel in item[config.RELATIONS]) + 1
            new_label['id'] = relation_id
            item[config.RELATIONS].append(new_label)
        else:
            return JsonResponse({'status': 'error', 'message': '未知标注类型'})
        # 保存回data.json
        with data_file.open('w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'添加标注失败: {str(e)}'})
