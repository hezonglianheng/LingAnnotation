from django.urls import path
from . import views

app_name = 'details'

urlpatterns = [
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('upload/<int:task_id>/', views.upload_data, name='upload_data'),
    path('download/<int:task_id>/', views.download_data, name='download_data'),
    path('info_edit/<int:task_id>/', views.update_task_info, name='update_task_info'),
    path('item_delete/', views.delete_task_item, name='delete_task_item'),
    # 07-02新增：增加展示item的路径
    path('showitem/<int:task_id>/<int:item_id>/', views.show_item, name='show_item'),
    # 07-03新增：前端标注添加接口
    path('showitem/<int:task_id>/<int:item_id>/add_label/', views.add_label, name='add_label'),
    # 07-03新增：前端标注删除接口
    path('showitem/<int:task_id>/<int:item_id>/delete_label/', views.delete_label, name='delete_label'),
    # 07-02新增：增加创建label的页面显示路径
    path('label_create/<int:task_id>/', views.label_create_page, name='label_create'),
    path('label_creation/', views.label_creation, name='label_creation'), 
    path('get_labels/', views.get_labels, name='get_labels'),
    path('remove_labels/', views.remove_labels, name='remove_labels'),
    # tag二值切换接口
    path('showitem/<int:task_id>/<int:item_id>/add_tag/', views.add_tag, name='add_tag'),
    path('showitem/<int:task_id>/<int:item_id>/delete_tag/', views.delete_tag, name='delete_tag'),
    # 07-04: 专门的关系标注页面和接口
    path('showitem/<int:task_id>/<int:item_id>/add_relation_page/', views.add_relation_page, name='add_relation_page'),
    path('showitem/<int:task_id>/<int:item_id>/add_relation/', views.add_relation, name='add_relation'),
    # 07-09: 关系删除接口
    path('showitem/<int:task_id>/<int:item_id>/delete_relation/', views.delete_relation, name='delete_relation'),
]