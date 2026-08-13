from django.shortcuts import redirect
from django.contrib import messages


def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if not request.user.is_manager():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:employee_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper