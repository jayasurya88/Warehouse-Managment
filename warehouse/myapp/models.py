from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.
class CustomUser(AbstractUser):
    user_type = models.CharField(default='1', max_length=10)  # Assuming user_type can be a string
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    pan_card = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=30)  # Added field for first name
    last_name = models.CharField(max_length=30)   # Added field for last name
    address = models.TextField()  # Added field for address
    is_approved = models.BooleanField(default=False)
def get_full_name(self):
        # Return the user's full name
        return f"{self.first_name} {self.last_name}".strip()

class Category(models.Model):
    category_name=models.CharField(max_length=255)



class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    specifications = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    pimg=models.ImageField(upload_to="images/",null=True)
    


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.quantity * self.prod.price

    def __str__(self):
        return f"Cart Item: {self.prod.name} (Quantity: {self.quantity})"
import random
import string   

def generate_tracking_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


class Order(models.Model):
    PENDING = 'pending'
    DISPATCHED = 'dispatched'
    IN_TRANSIT = 'intransit'
    DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (DISPATCHED, 'Dispatched'),
        (IN_TRANSIT, 'In Transit'),
        (DELIVERED, 'Delivered'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    tracking_id = models.CharField(max_length=12, default=generate_tracking_id, unique=True)
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    delivery_method = models.CharField(max_length=50, null=True, blank=True) 
    shipping_method = models.CharField(max_length=50, default='standard')  # Default set here
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)  # Default to PENDING
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='deliveries')
    location = models.CharField(max_length=255, blank=True, null=True)
    dispatch_location = models.CharField(max_length=255, blank=True, null=True)
    transmit_location = models.CharField(max_length=255, blank=True, null=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    client_marked_completed = models.BooleanField(default=False)
    delivery_person_marked_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"