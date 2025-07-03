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
    # 07-02新增：增加创建label的页面显示路径
    path('label_create/<int:task_id>/', views.label_create_page, name='label_create'),
    path('label_creation/', views.label_creation, name='label_creation'), 
    path('get_labels/', views.get_labels, name='get_labels'),
    path('delete_labels/', views.delete_labels, name='delete_labels'),
]