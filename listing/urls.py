from django.urls import path
from . import views

app_name = 'listing'

urlpatterns = [
    path('', views.index, name='index'),
    path('task_create/', views.task_create, name='task_create'),
    path('create_complete/', views.create_complete, name='create_complete'),
    # You can add other URL patterns for your listing app here
    path('task_delete/', views.task_delete, name='task_delete'),
]