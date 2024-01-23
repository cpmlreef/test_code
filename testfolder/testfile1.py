# django_codedd/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('api/get_git_url', views.get_git_path, name='get_git_url'),
    path('user_audits/', views.get_user_audits, name='user_audits'),
    path('audit_details/<uuid:audit_uuid>/', views.audit_details, name='audit-details'),
    path('flags/<uuid:audit_uuid>/', views.flags, name='flags'),
    path('dependencies/<uuid:audit_uuid>/', views.fetch_dependency_data, name='dependencies'),
    path('validate_git_url', views.validate_git_url, name='validate_git_url'),
    path('set_csrf_token/', views.set_csrf_token, name='set_csrf_token'),
    path('audit_scope_selector/<uuid:audit_uuid>/', views.get_audit_scope_views, name='get_audit_scope'),
    path('audit_scope_selector/', views.post_audit_scope_views, name='post_audit_scope'),
    path('api/store_file_selection/', views.store_file_selection, name='store_file_selection'),
    path('api/trigger_main_process/', views.trigger_main_process, name='trigger_main_process'),
    path('api/audit_scope_summary/<uuid:audit_uuid>/', views.audit_scope_summary, name='audit_scope_summary'),
    path('api/file_list/<uuid:audit_uuid>/', views.get_file_list, name='file_list'),
    path('api/file_detail/<path:file_path>/', views.get_file_details, name='file_detail'),
]
