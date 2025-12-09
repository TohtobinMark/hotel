from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, User, UserRole, Booking, Guest, Category, Room, ServiceProvision


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Валидация
        errors = []
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.email}!')

                # Redirect based on user role
                if user.role == UserRole.ADMIN:
                    return redirect('admin')
                elif user.role == UserRole.MANAGER:
                    return redirect('manager')
                elif user.role == UserRole.CLIENT:
                    return redirect('services_list')
                else:
                    return redirect('services_list')
            else:
                messages.error(request, 'Invalid email or password.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def services_list(request):
    services = Service.objects.all()
    return render(request, 'services/list.html', {
        'services': services,
        'user': request.user
    })



@login_required
def manager(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')
    clients = User.objects.filter(role='client')
    return render(request, 'users/manager/manager.html', {'clients': clients})

@login_required
def client(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.CLIENT]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')
    return render(request, 'users/client.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')

        errors = []
        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if User.objects.filter(email=email).exists():
            errors.append('User with this email already exists')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=full_name,
                    phone_number=phone_number,
                    role=UserRole.CLIENT
                )
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')

    return render(request, 'auth/register.html')

@login_required
def manager_dashboard(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')

    total_clients = User.objects.filter(role=UserRole.CLIENT).count()
    total_services = Service.objects.count()
    total_rooms = Room.objects.count()
    active_bookings = Booking.objects.filter(
        check_in_date__lte=timezone.now().date(),
        check_out_date__gte=timezone.now().date()
    ).count()

    return render(request, 'users/manager/manager_dashboard.html', {
        'total_clients': total_clients,
        'total_services': total_services,
        'total_rooms': total_rooms,
        'active_bookings': active_bookings
    })

@login_required
def manager_clients(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')

    clients = User.objects.filter(role=UserRole.CLIENT)
    return render(request, 'users/manager/manager_clients.html', {'clients': clients})