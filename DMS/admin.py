from django.contrib import admin
from .models import User, Client, Courier, Storekeeper, Product, Article, Order, OrderItem, Delivery, Notification, Review

# Custom admin for User model to handle custom fields
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_client', 'is_courier', 'is_storekeeper', 'is_admin')
    search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Client, ClientAdmin)

class CourierAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'vehicle_details')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Courier, CourierAdmin)

class StorekeeperAdmin(admin.ModelAdmin):
    list_display = ('user', 'warehouse_location')
    search_fields = ('user__username', 'warehouse_location')

admin.site.register(Storekeeper, StorekeeperAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

admin.site.register(Product, ProductAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'client', 
        'created_at', 
        'get_products', 
        'get_pickup_address', 
        'get_destination_address'
    )
    list_filter = ('client', 'created_at')  # Removed 'products' for now

    def get_products(self, obj):
        # Ensure `products` is a ManyToManyField
        return ", ".join([p.name for p in obj.products.all()]) if obj.products.exists() else "No Products"
    get_products.short_description = 'Products'

    def get_pickup_address(self, obj):
        return obj.pickup_address if obj.pickup_address else 'N/A'
    get_pickup_address.short_description = 'Pickup Address'

    def get_destination_address(self, obj):
        return obj.destination_address if obj.destination_address else 'N/A'
    get_destination_address.short_description = 'Destination Address'

admin.site.register(Article, ArticleAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

from django.contrib import admin
from .models import ProductType

class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Adjust this to your actual fields
    list_filter = ('name',)
    search_fields = ('name',)
admin.site.register(ProductType, ProductTypeAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('client', 'total_price', 'payment_status', 'delivery_status', 'created_at')
    search_fields = ('client__user__username',)
    list_filter = ('payment_status', 'delivery_status')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'start_time', 'end_time', 'status')
    search_fields = ('order__client__user__username', 'courier__user__username')
    list_filter = ('status',)

admin.site.register(Delivery, DeliveryAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'created_at', 'read', 'status', 'order')
    list_filter = ('read', 'status', 'created_at', 'order')
    search_fields = ('message', 'order__id')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'comment')
    search_fields = ('order__client__user__username', 'rating')
    list_filter = ('rating',)

admin.site.register(Review, ReviewAdmin)
