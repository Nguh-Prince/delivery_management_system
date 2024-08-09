# core/serializers.py

from rest_framework import serializers
from .models import User, Client, Courier, Storekeeper, Product, Article, Order, OrderItem, Delivery, Notification, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_client', 'is_courier', 'is_storekeeper', 'is_admin']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['user', 'phone_number', 'address']

class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['user', 'phone_number', 'vehicle_details']

class StorekeeperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storekeeper
        fields = ['user', 'warehouse_location']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'client', 'name', 'description', 'pickup_address', 'destination_address', 'delivery_status']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'client', 'products', 'total_price', 'payment_status', 'delivery_status', 'qr_code', 'delivery_address', 'created_at', 'updated_at', 'order_items']

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'courier', 'start_time', 'end_time', 'status']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'status']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'order', 'rating', 'comment']
