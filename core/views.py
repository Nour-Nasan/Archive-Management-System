from django.shortcuts import redirect


def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_manager():
            return redirect('dashboard:manager_dashboard')
        return redirect('dashboard:employee_dashboard')

    return redirect('accounts:login')