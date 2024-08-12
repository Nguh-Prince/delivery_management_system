from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_client = models.BooleanField(default=False)
    is_courier = models.BooleanField(default=False)
    is_storekeeper = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_manage_couriers", "Can manage couriers"),
            ("can_manage_storekeepers", "Can manage storekeepers"),
            ("can_manage_clients", "Can manage clients"),
            ("can_view_overall_info", "Can view overall information"),
            ("can_manage_articles", "Can manage articles"),
            ("can_notify_courier", "Can notify courier"),
            ("can_manage_refunds", "Can manage refunds"),
            ("can_view_deliveries", "Can view deliveries"),
            ("can_manage_deliveries", "Can manage deliveries"),
            ("can_make_orders", "Can make orders"),
            ("can_get_articles_delivered", "Can get articles delivered"),
            ("can_decline_orders", "Can decline orders"),
            ("can_view_cart", "Can view cart"),
            ("can_add_to_cart", "Can add to cart"),
        ]

class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    def __str__(self):
        return self.user.username
    
    @property
    def name(self):
        return self.user.username

class Courier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    vehicle_details = models.CharField(max_length=100, default=None)
    def __str__(self):
        return self.user.username

class Adresse(models.Model):
    town = models.CharField(max_length=100)
    quarter = models.CharField(max_length=100)
    fees = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quarter}, {self.town}"

class Storekeeper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    warehouse_location = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/')
    def __str__(self):
        return self.name
class ProductType(models.Model):

    name = models.CharField(max_length=150)

    def __str__(self):
            return self.name

class Article(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sender_town = models.ForeignKey(Adresse, related_name='sender_town', on_delete=models.CASCADE)
    sender_quarter = models.ForeignKey(Adresse, related_name='sender_quarter', on_delete=models.CASCADE)
    receiver_town = models.ForeignKey(Adresse, related_name='receiver_town', on_delete=models.CASCADE)
    receiver_quarter = models.ForeignKey(Adresse, related_name='receiver_quarter', on_delete=models.CASCADE)
    sender_phone = models.CharField(max_length=15)
    receiver_phone = models.CharField(max_length=15)
    weight = models.FloatField()
    products = models.ManyToManyField(Product, blank=True)
    delivery_status = models.CharField(max_length=20, default='Pending')  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Article #{self.id} for {self.client.user.username}"

    @property
    def pickup_address(self):
        return self.sender_quarter

    @property
    def destination_address(self):
        return self.receiver_quarter
    
class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    delivery_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered'), ('Declined', 'Declined')])
    qr_code = models.CharField(max_length=100)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.client.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')])

class Notification(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey('Courier', on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=20)
    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.CASCADE, related_name='notifications')
    def __str__(self):
        return f"Notification to {self.receiver.user.username} - {self.message[:50]}"

class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    approved = models.BooleanField(default=False)

class Cart(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
