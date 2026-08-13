from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import manager_required


@login_required
@manager_required
def manager_dashboard(request):
    return render(request, 'dashboard/manager_dashboard.html')


@login_required
def employee_dashboard(request):
    return render(request, 'dashboard/employee_dashboard.html')