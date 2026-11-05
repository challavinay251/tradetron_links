
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CustomUser


# ==========================================
# LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:

        if not request.user.is_active:
            logout(request)
            messages.error(request, 'Your account is inactive.')
            return redirect('login')

        if not request.user.is_approved:
            logout(request)
            messages.warning(
                request,
                'Your account is waiting for admin approval.'
            )
            return redirect('login')

        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_active:
                messages.error(
                    request,
                    'Your account is inactive.'
                )
                return redirect('login')

            if not user.is_approved:
                messages.warning(
                    request,
                    'Your account is waiting for admin approval.'
                )
                return redirect('login')

            login(request, user)

            if user.role == 'ADMIN':
                return redirect('admin_dashboard')

            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(request, 'accounts/login.html')


# ==========================================
# REGISTRATION
# ==========================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get(
            'username', ''
        ).strip()

        email = request.POST.get(
            'email', ''
        ).strip()

        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:

            messages.error(
                request,
                'All fields are required.'
            )

        elif CustomUser.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

        elif CustomUser.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

        elif password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

        elif len(password) < 8:

            messages.error(
                request,
                'Password must contain at least 8 characters.'
            )

        else:

            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='USER',
                is_approved=False
            )

            messages.success(
                request,
                'Registration successful! Wait for admin approval.'
            )

            return redirect('login')

    return render(request, 'accounts/register.html')


# ==========================================
# LOGOUT
# ==========================================

@login_required
@require_POST
def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('login')
