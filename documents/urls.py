from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('add/', views.document_create, name='document_create'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('<int:pk>/upload-version/', views.document_upload_version, name='document_upload_version'),
]
