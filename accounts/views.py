from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, CreateUserForm, EditUserForm, ChangeEmailForm, ChangePasswordForm
from .models import CustomUser, ActivityLog


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        
        # Log successful login
        ip_address = get_client_ip(request)
        ActivityLog.objects.create(
            user=user,
            action='login',
            description=f"User {user.email} ({user.get_full_name()}) logged in from {ip_address}",
            affected_entity=f"User: {user.email}",
            ip_address=ip_address,
            status='success'
        )
        
        # Redirect based on user role immediately
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'registra':
            return redirect('registra_dashboard')
        elif user.role == 'professor':
            return redirect('professor_dashboard')
        return redirect('dashboard')
    
    # Don't pass form to template with display of messages (we'll not show notifications on login)
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
            user = form.save(commit=False)
            # Auto-generate username from email (remove domain part)
            email_local = user.email.split('@')[0]
            user.username = email_local
            user.save()
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


@login_required
def edit_user(request, user_id):
    if not request.user.is_admin():
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('user_list')
    
    form = EditUserForm(request.POST or None, instance=user)
    
    if request.method == 'POST':
        if form.is_valid():
            user_obj = form.save(commit=False)
            # Auto-update username from email if email changed
            email_local = user_obj.email.split('@')[0]
            user_obj.username = email_local
            user_obj.save()
            messages.success(request, f"User {user_obj.get_full_name()} has been updated successfully.")
            return redirect('user_list')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return render(request, 'admin_panel/edit_user.html', {'form': form, 'user': user})


@login_required
def manage_profile(request):
    """Manage own profile - view personal information"""
    user = request.user
    return render(request, 'accounts/manage_profile.html', {'user': user})


@login_required
def change_email(request):
    """Change own email address"""
    user = request.user
    form = ChangeEmailForm(request.POST or None, instance=user)
    
    if request.method == 'POST':
        if form.is_valid():
            old_email = user.email
            new_email = form.cleaned_data['email']
            
            user_obj = form.save(commit=False)
            # Update username from new email
            email_local = new_email.split('@')[0]
            user_obj.username = email_local
            user_obj.save()
            
            # Log the action
            ip_address = get_client_ip(request)
            ActivityLog.objects.create(
                user=user,
                action='profile_update',
                description=f"Email changed from {old_email} to {new_email}",
                affected_entity=f"User: {user.email}",
                ip_address=ip_address,
                status='success'
            )
            
            messages.success(request, f"Your email has been updated successfully to {new_email}")
            return redirect('manage_profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return render(request, 'accounts/change_email.html', {'form': form})


@login_required
def change_password(request):
    """Change own password"""
    user = request.user
    form = ChangePasswordForm(user, request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # Keep session alive after password change
            update_session_auth_hash(request, user)
            
            # Log the action
            ip_address = get_client_ip(request)
            ActivityLog.objects.create(
                user=user,
                action='profile_update',
                description=f"Password changed",
                affected_entity=f"User: {user.email}",
                ip_address=ip_address,
                status='success'
            )
            
            messages.success(request, "Your password has been updated successfully")
            return redirect('manage_profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    
    return render(request, 'accounts/change_password.html', {'form': form})
