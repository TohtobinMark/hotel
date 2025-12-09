from hotel import views
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('services/', views.services_list, name='services_list'),
    path('admin/', admin.site.urls),
    path('users/manager/', views.manager, name='manager'),
    path('users/client/', views.client, name='client'),
    path('manager/', views.manager_dashboard, name='manager'),
    path('manager/clients/', views.manager_clients, name='manager_clients'),
    path('manager/services/', views.manager_services, name='manager_services'),
    path('manager/rooms/', views.manager_rooms, name='manager_rooms'),
path('manager/add-service/', views.add_service, name='add_service'),
]