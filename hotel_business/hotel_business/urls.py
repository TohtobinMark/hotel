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
    path('users/client/', views.client, name='client')
]