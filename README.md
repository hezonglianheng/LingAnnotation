# LingAnnotation
2025《中文信息处理专题》课程作业：语言信息标注管理系统

## 鸣谢
本程序来源于[@Dylandjk](https://github.com/Dylandjk)的[myproject](https://github.com/Dylandjk/myproject)项目，为便于管理而设置本仓库，在此表示感谢。

本程序只用于学术研究目的，遵循GPL3.0开源协议。

## 环境要求
- Python版本：[3.7.8](https://www.python.org/downloads/release/python-378/)
- Django版本：[3.0.5](https://docs.djangoproject.com/en/3.0/)

## 项目简介
LingAnnotation是一个基于Django的语言学数据标注管理系统，支持对文本语料进行多层次标注，包括：
- **Tag标注**：对整个句子/文档进行分类标注
- **Label标注**：对文本片段进行实体或语言现象标注  
- **Relation标注**：标注标签之间或标签与关系之间的语义关系

## 安装与配置

### 1. 克隆项目
```bash
git clone <项目地址>
cd LingAnnotation
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

### 5. 启动服务
```bash
python manage.py runserver
```

服务启动后，访问 `http://127.0.0.1:8000` 即可使用系统。

## 使用指南

### 1. 创建标注任务
1. 在首页点击"创建新任务"
2. 填写任务名称和描述
3. 点击"确定"完成任务创建

### 2. 上传语料数据
1. 进入任务详情页面
2. 点击"上传数据"按钮
3. 选择JSON或TXT格式的语料文件
4. 系统将自动解析并导入语料

### 3. 配置标注类型
1. 在任务详情页面点击"编辑标签"
2. 可以添加三种类型的标注：
   - **Tag标签**：用于对整个文档进行分类
   - **Label标注**：用于标注文本中的片段
   - **Relation关系**：用于建立标签间的关系
3. 为每种标注类型设置名称和颜色

### 4. 进行标注
1. 点击语料列表中的"详情"按钮进入标注界面
2. **文本标签**：点击可用标签类型直接切换
3. **片段标注**：
   - 选中要标注的文本片段
   - 点击相应的标注类型进行标注
4. **关系标注**：
   - 点击"建立关系"按钮
   - 选择两个标注对象
   - 选择关系类型
   - 确认建立关系

### 5. 导出数据
1. 在任务详情页面点击"下载数据"
2. 系统将打包所有标注数据为ZIP文件
3. 包含的文件：
   - `data.json`：标注数据和原文
   - `tag.json`：Tag标签类型集
   - `label.json`：Label标注类型集  
   - `relation.json`：关系标注类型集

## 数据格式说明

### data.json 结构
```json
[
  {
    "id": "唯一标识符",
    "text": "原始文本内容",
    "tags": ["tag1", "tag2"],
    "labels": [
      {
        "start": 0,
        "end": 5,
        "type": "标注类型",
        "text": "标注文本"
      }
    ],
    "relations": [
      {
        "relation_id": "关系ID",
        "type": "关系类型",
        "start": {...},
        "end": {...}
      }
    ]
  }
]
```

### 标签配置文件结构
- `tag.json`：`[{"name": "名称", "color": "#颜色值"}]`
- `label.json`：`[{"name": "名称", "color": "#颜色值"}]`
- `relation.json`：`[{"name": "名称", "color": "#颜色值"}]`

## 功能特性
- ✅ 多任务管理
- ✅ 多种标注类型支持
- ✅ 可视化标注界面
- ✅ 数据导入导出
- ✅ 响应式设计

## 技术架构
- **后端**：Django 3.0.5
- **前端**：Bootstrap 4 + jQuery
- **数据库**：SQLite（可配置其他数据库）
- **存储**：本地文件系统

## 常见问题

### Q: 如何删除标注？
A: 在标注详情页面，每个标注右侧都有删除按钮，点击即可删除。删除Label标注时，相关的关系也会被自动删除。

### Q: 支持哪些文件格式？
A: 目前支持JSON和TXT格式的语料文件。JSON文件需要符合系统定义的数据结构。

### Q: 如何备份数据？
A: 使用"下载数据"功能可以导出完整的标注数据，建议定期备份。

## 开发说明
如需进行二次开发，请参考Django官方文档。主要应用模块：
- `listing`：任务管理模块
- `details`：标注功能模块
- `utils`：工具函数模块

## 许可证
本项目采用GPL 3.0开源许可证，仅供学术研究使用。
