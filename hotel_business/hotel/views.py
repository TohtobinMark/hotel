from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, User, UserRole, Booking, Category, Room, ServiceProvision, Document


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
    services = Service.objects.filter(is_active=True).all()
    user_data = None
    services_with_discount = []
    for service in services:
        discounted_price = service.cost
        if request.user.is_authenticated and request.user.role == 'client':
            discounted_price = request.user.calculate_price_with_discount(service.cost)

            services_with_discount.append({
                'service': service,
                'original_price': service.cost,
                'discounted_price': discounted_price,
                'has_discount': request.user.discount > 0 if request.user.is_authenticated else False,
            })
    if request.user.is_authenticated:
        # Для всех авторизованных пользователей
        user_data = {
            'discount': float(request.user.discount),
            'has_discount': request.user.discount > 0,
            'discount_more_than_10': request.user.discount > 10,
            'is_guest': request.user.role == UserRole.GUEST
        }
    else:
        # Для неавторизованных гостей
        user_data = {
            'discount': 0,
            'has_discount': False,
            'discount_more_than_10': False,
            'is_guest': True
        }
    return render(request, 'services/list.html', {
        'services': services,
        'user': request.user,
        'user_data': user_data,
        'services_with_discount': services_with_discount
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

@login_required
def manager_services(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')
    search_query = request.GET.get('search', '')
    services = Service.objects.all()
    if search_query:
        services = services.filter(name__icontains=search_query)

    return render(request, 'users/manager/manager_services.html', {
        'services': services,
        'search_query': search_query
    })

@login_required
def manager_rooms(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')

    rooms = Room.objects.select_related('category').prefetch_related('category__equipment__item')
    categories = Category.objects.all()
    bed_filter = request.GET.get('bed_count', '')
    category_filter = request.GET.get('category', '')

    if bed_filter:
        if bed_filter == '4':
            rooms = rooms.filter(bed_count__gte=4)
        else:
            rooms = rooms.filter(bed_count=bed_filter)

    if category_filter:
        rooms = rooms.filter(category_id=category_filter)

    return render(request, 'users/manager/manager_rooms.html', {
        'rooms': rooms,
        'categories': categories,
        'bed_filter': bed_filter,
        'category_filter': category_filter,
        'bed_counts': bed_counts
    })

@login_required
def add_service(request):
    if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        messages.error(request, 'Access denied.')
        return redirect('services_list')
#ddd
    if request.method == 'POST':
        try:
            guest_id = request.POST.get('guest_id')
            service_id = request.POST.get('service_id')
            service_date = request.POST.get('service_date')
            quantity = int(request.POST.get('quantity', 1))

            # Получаем объекты
            guest = get_object_or_404(User, id=client_id, role=UserRole.CLIENT)
            service = get_object_or_404(Service, id=service_id)

            # Находим активное бронирование гостя
            today = timezone.now().date()
            booking = Booking.objects.filter(
                guest=client,
                check_in_date__lte=today,
                check_out_date__gte=today
            ).first()

            if not booking:
                messages.error(request, 'У гостя нет активного бронирования')
                return redirect('assign_service')

            existing_provision = ServiceProvision.objects.filter(
                booking=booking,
                service=service,
                service_date=service_date
            ).first()

            if existing_provision:
                existing_provision.quantity += quantity
                existing_provision.save()
                messages.success(request, f'Количество услуги "{service.name}" обновлено для гостя {guest.full_name}')
            else:
                service_provision = ServiceProvision.objects.create(
                    booking=booking,
                    service=service,
                    quantity=quantity,
                    service_date=service_date
                )
                messages.success(request, f'Услуга "{service.name}" успешно назначена гостю {guest.full_name}')
                return redirect('assign_service')

        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    clients = User.objects.filter(role=UserRole.CLIENT)
    services = Service.objects.all()

    return render(request, 'users/manager/add_service.html', {
        'clients': clients,
        'services': services
    })