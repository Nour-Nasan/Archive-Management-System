from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import manager_required, superuser_required
from .forms import UserCreateForm, RegistrationForm, ProfileEditForm
from .models import User, Role


# ─── Public: Login ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'accounts/login.html')

        # Superusers bypass approval check
        if not user.is_superuser:
            if user.approval_status == User.APPROVAL_PENDING:
                messages.warning(
                    request,
                    'Your account is awaiting approval by the System Administrator. '
                    'You will be notified once access is granted.',
                )
                return render(request, 'accounts/login.html')

            if user.approval_status == User.APPROVAL_REJECTED:
                messages.error(
                    request,
                    'Your account registration has been rejected. '
                    'Please contact the System Administrator for more information.',
                )
                return render(request, 'accounts/login.html')

        login(request, user)
        return _redirect_after_login(user)

    return render(request, 'accounts/login.html')


def _redirect_after_login(user):
    if user.is_manager():
        return redirect('dashboard:manager_dashboard')
    return redirect('dashboard:employee_dashboard')


# ─── Public: Register ─────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request.user)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created successfully! Your request is pending approval '
                'by the System Administrator. You will be able to log in once approved.',
            )
            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ─── Auth ─────────────────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ─── System Administrator: User Management ────────────────────────────────────

@superuser_required
def user_list(request):
    users = (
        User.objects
        .select_related('role')
        .exclude(pk=request.user.pk)   # admin cannot manage their own account here
        .order_by('-date_joined')
    )
    roles = Role.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})


@superuser_required
def user_approve(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        _guard_self(request, user)
        user.approval_status = User.APPROVAL_APPROVED
        user.save(update_fields=['approval_status'])
        messages.success(request, f'Account "{user.username}" has been approved.')
    return redirect('accounts:user_list')


@superuser_required
def user_reject(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        _guard_self(request, user)
        user.approval_status = User.APPROVAL_REJECTED
        user.save(update_fields=['approval_status'])
        messages.success(request, f'Account "{user.username}" has been rejected.')
    return redirect('accounts:user_list')


@superuser_required
def user_toggle_active(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        _guard_self(request, user)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        state = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'Account "{user.username}" has been {state}.')
    return redirect('accounts:user_list')


@superuser_required
def user_set_role(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        _guard_self(request, user)
        role_id = request.POST.get('role_id')
        if role_id:
            role = get_object_or_404(Role, pk=role_id)
            user.role = role
            user.save(update_fields=['role'])
            messages.success(request, f'Role updated for "{user.username}".')
        else:
            messages.error(request, 'No role selected.')
    return redirect('accounts:user_list')


@login_required
@manager_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form})


# ─── My Profile / Account Settings ───────────────────────────────────────────

@login_required
def profile_edit(request):
    """Any authenticated user can update their own first name, last name, and email."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile_edit')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    """Any authenticated user can change their own password.
    Uses update_session_auth_hash so the session remains valid after the change.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile_edit')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _guard_self(request, target_user):
    """Prevent admin from accidentally modifying their own account via these actions."""
    if target_user.pk == request.user.pk:
        raise PermissionError('Cannot modify your own account via user management.')
