from django.shortcuts import render

# Create your views here.
from . import utils, config
from listing.models import TaskRecord
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from pathlib import Path
import json
import zipfile
import os
from typing import Dict, Any

def task_detail(request, task_id):
    # Fetch the task record from the database using the task_id
    task_record = TaskRecord.objects.get(task_id=task_id)
    task_dirpath = task_record.task_dirpath
    print(task_dirpath)
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
            print(task_id, item_id)
            
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
        print(file_path)
        with file_path.open("r", encoding='utf-8') as f:
            data = json.load(f)
        
        print(data[0])
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
            if last_end < start:
                segments.append({'text': text[last_end:start], 'label': None})
            segments.append({'text': text[start:end], 'label': label})
            last_end = end
        if last_end < len(text):
            segments.append({'text': text[last_end:], 'label': None})

        return render(request, 'details/showitem.html', {'task': task_record, 'item': item, 'segments': segments})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"显示条目失败: {str(e)}"})