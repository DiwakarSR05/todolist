from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('task/<int:pk>/toggle/', views.toggle_task_completion, name='toggle_task_completion'),
    path('task/quick_add/', views.quick_add_task, name='quick_add_task'),
    path('category/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile_view/', views.profile_view, name='profile_view'),
]