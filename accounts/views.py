from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, CreateUserForm
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # Redirect based on user role immediately
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'registra':
            return redirect('registra_dashboard')
        elif user.role == 'professor':
            return redirect('professor_dashboard')
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'registra':
        return redirect('registra_dashboard')
    elif user.role == 'professor':
        return redirect('professor_dashboard')
    return redirect('login')


@login_required
def create_user(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    form = CreateUserForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.get_full_name()} ({user.get_role_display()})")
            return redirect('admin_dashboard')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return render(request, 'admin_panel/create_user.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.is_admin():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    users = CustomUser.objects.exclude(id=request.user.id).order_by('role', 'last_name')
    return render(request, 'admin_panel/user_list.html', {'users': users})


@login_required
def toggle_user_active(request, user_id):
    if not request.user.is_admin():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect('user_list')
