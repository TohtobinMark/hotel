from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _

class Document(models.Model):
    series = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    issue_date = models.DateField()
    issued_by = models.CharField(max_length=255)

class Guest(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="guests")
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField()
    discount = models.DecimalField(max_digits=5, decimal_places=2,default=0)

class Category(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

class Room(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="rooms")
    floor = models.IntegerField()
    room_count = models.IntegerField()
    bed_count = models.IntegerField()

class Booking(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Service(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

class ServiceProvision(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="service_provisions")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_provisions")
    quantity = models.IntegerField(default=1)
    service_date = models.DateField()

class Item(models.Model):
    name = models.CharField(max_length=255)

class Equipment(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="equipment")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="equipment")

class UserRole(models.TextChoices):
    GUEST = 'guest'
    CLIENT = 'client'
    MANAGER = 'manager'
    ADMIN = 'admin'

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.GUEST)
    phone_number = models.CharField(max_length=20, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()