from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_manager():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:employee_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superuser:
            messages.error(request, 'This area is restricted to the System Administrator.')
            if request.user.is_manager():
                return redirect('dashboard:manager_dashboard')
            return redirect('dashboard:employee_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
