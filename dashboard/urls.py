from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('manager/',  views.manager_dashboard, name='manager_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('reports/',  views.reports,            name='reports'),
]
