# 文件存储位置标注
本位置存储所有的标注文件，目录为标注项目的名称，文件为**JSON**格式.

## 文件夹内容
每个文件夹由4个**JSON**文件构成：
- data.json: 标注数据，包括原文以及标注信息
- tag.json: 对句子整体进行标注的标签集文件
- label.json: 对句子中的slice进行标注的标签集文件
- relation.json: 对label, relation之间的关系进行标注的标签集文件