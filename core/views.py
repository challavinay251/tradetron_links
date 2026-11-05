
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import TradeTronSettings


User = get_user_model()


# ==========================================
# USER ACCESS DECORATOR
# ==========================================

def approved_user_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        user = request.user

        if not user.is_active or not user.is_approved:
            return redirect('login')

        if user.role != 'USER':
            return redirect('admin_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================
# ADMIN ACCESS DECORATOR
# ==========================================

def admin_user_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        user = request.user

        if not user.is_active or not user.is_approved:
            return redirect('login')

        if user.role != 'ADMIN':
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================
# USER HOME PAGE
# ==========================================

@approved_user_required
def home(request):

    tradetron_settings = TradeTronSettings.objects.filter(
        pk=1
    ).first()

    context = {
        'tradetron_settings': tradetron_settings,
    }

    return render(
        request,
        'core/home.html',
        context
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@admin_user_required
def admin_dashboard(request):

    users = User.objects.filter(
        is_superuser=False,
        is_staff=False,
        role='USER'
    ).order_by('-date_joined')

    # Search users by username or email
    search = request.GET.get('search', '').strip()

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )

    # Dashboard statistics
    total_users = User.objects.filter(
        is_superuser=False,
        role='USER'
    ).count()

    pending_users = User.objects.filter(
        is_superuser=False,
        role='USER',
        is_approved=False,
        is_active=True
    ).count()

    approved_users = User.objects.filter(
        is_superuser=False,
        role='USER',
        is_approved=True,
        is_active=True
    ).count()

    inactive_users = User.objects.filter(
        is_superuser=False,
        role='USER',
        is_active=False
    ).count()

    # Get or create the single TradeTron settings record
    tradetron_settings, created = TradeTronSettings.objects.get_or_create(
        pk=1
    )

    context = {
        'users': users,
        'total_users': total_users,
        'pending_users': pending_users,
        'approved_users': approved_users,
        'inactive_users': inactive_users,
        'search': search,
        'tradetron_settings': tradetron_settings,
    }

    return render(
        request,
        'core/admin_dashboard.html',
        context
    )


# ==========================================
# ADMIN USER MANAGEMENT
# ==========================================

@admin_user_required
@require_POST
def manage_users(request):

    action = request.POST.get('action')

    # --------------------------------------
    # ADD NEW USER
    # --------------------------------------

    if action == 'add':

        username = request.POST.get(
            'username', ''
        ).strip()

        email = request.POST.get(
            'email', ''
        ).strip()

        password = request.POST.get(
            'password', ''
        )

        if not username or not email or not password:

            messages.error(
                request,
                'All fields are required.'
            )

        elif len(password) < 8:

            messages.error(
                request,
                'Password must contain at least 8 characters.'
            )

        elif User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

        elif User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                'Email already exists.'
            )

        else:

            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='USER',
                is_approved=False
            )

            messages.success(
                request,
                f'User {username} created successfully. Waiting for approval.'
            )

        return redirect('admin_dashboard')

    # --------------------------------------
    # GET EXISTING USER
    # --------------------------------------

    user_id = request.POST.get('user_id')

    if not user_id:

        messages.error(
            request,
            'User ID is missing.'
        )

        return redirect('admin_dashboard')

    target = get_object_or_404(
        User,
        pk=user_id,
        is_superuser=False,
        is_staff=False,
        role='USER'
    )

    # Prevent modifying own account
    if target == request.user:

        messages.error(
            request,
            'You cannot modify your own account here.'
        )

        return redirect('admin_dashboard')

    # --------------------------------------
    # APPROVE USER
    # --------------------------------------

    if action == 'approve':

        target.is_approved = True
        target.is_active = True
        target.save()

        messages.success(
            request,
            f'{target.username} has been approved successfully.'
        )

    # --------------------------------------
    # REVOKE USER ACCESS
    # --------------------------------------

    elif action == 'revoke':

        target.is_approved = False
        target.save()

        messages.success(
            request,
            f'Access revoked for {target.username}.'
        )

    # --------------------------------------
    # DEACTIVATE USER
    # --------------------------------------

    elif action == 'deactivate':

        target.is_active = False
        target.save()

        messages.success(
            request,
            f'{target.username} has been deactivated.'
        )

    # --------------------------------------
    # ACTIVATE USER
    # --------------------------------------

    elif action == 'activate':

        target.is_active = True
        target.save()

        messages.success(
            request,
            f'{target.username} has been activated.'
        )

    # --------------------------------------
    # DELETE USER
    # --------------------------------------

    elif action == 'delete':

        username = target.username

        target.delete()

        messages.success(
            request,
            f'{username} has been deleted successfully.'
        )

    else:

        messages.error(
            request,
            'Invalid user management action.'
        )

    return redirect('admin_dashboard')


# ==========================================
# UPDATE TRADETRON SETTINGS
# ==========================================

@admin_user_required
@require_POST
def update_tradetron_settings(request):

    tradetron_settings, created = TradeTronSettings.objects.get_or_create(
        pk=1
    )

    url = request.POST.get(
        'tradetron_url', ''
    ).strip()

    is_enabled = request.POST.get('is_enabled') == 'on'

    # Validate URL
    if url:

        validator = URLValidator()

        try:
            validator(url)

        except ValidationError:

            messages.error(
                request,
                'Please enter a valid URL, including https://.'
            )

            return redirect('admin_dashboard')

    # Save settings
    tradetron_settings.url = url
    tradetron_settings.is_enabled = is_enabled

    tradetron_settings.save()

    messages.success(
        request,
        'TradeTron settings updated successfully.'
    )

    return redirect('admin_dashboard')
