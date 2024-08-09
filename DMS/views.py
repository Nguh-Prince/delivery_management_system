# core/views.py
from .utils import notify_courier
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import User,Cart,Adresse,OrderItem ,Refund, Client, Courier, Storekeeper, Product, Article, Order, Delivery, Notification, Review
from .serializers import UserSerializer, ClientSerializer, CourierSerializer, StorekeeperSerializer, ProductSerializer, ArticleSerializer, OrderSerializer, DeliverySerializer, NotificationSerializer, ReviewSerializer
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import DetailView, CreateView, TemplateView, View
import requests
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .forms import AdminUserCreationForm, DeliveryForm, ArticleForm, AddToCartForm,OrderForm, RefundForm, NotificationForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()
#TEMPLATES RENDERING
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'dms/product_list.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    client = request.user.client
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            Cart.objects.update_or_create(
                client=client,
                product=product,
                defaults={'quantity': quantity}
            )
            return redirect('cart')
    else:
        form = AddToCartForm()
    
    return render(request, 'dms/add_to_cart.html', {'form': form, 'product': product})

@login_required
def view_cart(request):
    client = request.user.client
    cart_items = Cart.objects.filter(client=client)
    return render(request, 'dms/dashboards/view_cart.html', {'cart_items': cart_items})
class ProductDetailView(DetailView):
    model = Product
    template_name = 'dms/product_detail.html'

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    client = Client.objects.get(user=request.user)
    
    # Try to get the cart item or create it with a default quantity of 1
    cart_item, created = Cart.objects.get_or_create(client=client, product=product, defaults={'quantity': 1})
    
    # If the cart item already exists, increment the quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('view_cart')

def load_quarters(request):
    town_name = request.GET.get('town')
    quarters = Adresse.objects.filter(town=town_name).order_by('quarter')
    return JsonResponse(list(quarters.values('id', 'quarter')), safe=False)

class OrderConfirmationView(TemplateView):
    template_name = 'dms/order_confirmation.html'

@method_decorator(login_required, name='dispatch')
class ManageCartView(View):
    template_name = 'dms/manage_cart.html'

    def get(self, request):
        cart_items = Cart.objects.filter(client=request.user.client)
        return render(request, self.template_name, {'cart_items': cart_items})

    def post(self, request):
        action = request.POST.get('action')
        if action == 'update':
            cart_item_id = request.POST.get('cart_item_id')
            cart_item = get_object_or_404(Cart, id=cart_item_id, client=request.user.client)
            form = AddToCartForm(request.POST, instance=cart_item)
            if form.is_valid():
                form.save()
        elif action == 'remove':
            cart_item_id = request.POST.get('cart_item_id')
            cart_item = get_object_or_404(Cart, id=cart_item_id, client=request.user.client)
            cart_item.delete()
        elif action == 'order':
            item_ids = request.POST.getlist('items_to_order')
            if item_ids:
                client = request.user.client
                order = Order(client=client)
                order.save()
                for item_id in item_ids:
                    cart_item = get_object_or_404(Cart, id=item_id, client=client)
                    # Create order items for each cart item
                    order.products.add(cart_item.product)
                    order.total_price += cart_item.product.price * cart_item.quantity
                    cart_item.delete()  # Remove items from cart after ordering
                return redirect('order_confirmation')  # Redirect to an order confirmation page

        return redirect('view_cart')
class ManageArticlesView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/manage_articles.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'client') or hasattr(self.request.user, 'storekeeper')
    
    def get(self, request, *args, **kwargs):
        # Determine if the user is a client or storekeeper and fetch appropriate articles
        if hasattr(request.user, 'client'):
            articles = Article.objects.filter(client=request.user.client).select_related('client').prefetch_related('products')
        elif hasattr(request.user, 'storekeeper'):
            articles = Article.objects.all().select_related('client').prefetch_related('products')
        else:
            return redirect('manage_articles')
        
        form = ArticleForm()  # Initialize the form
        return render(request, self.template_name, {'articles': articles, 'form': form})
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():  # Check if the request is an AJAX request
            town_id = request.POST.get('town')
            quarters = Adresse.objects.filter(town=town_id).order_by('quarter')
            return JsonResponse(list(quarters.values('id', 'quarter')), safe=False)
        
        # Handle normal form submission
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            if hasattr(request.user, 'client'):
                article.client = request.user.client
            article.save()
            return redirect('manage_articles')
        
        # Re-fetch the articles and render the form again if it's invalid
        if hasattr(request.user, 'client'):
            articles = Article.objects.filter(client=request.user.client).select_related('client').prefetch_related('products')
        elif hasattr(request.user, 'storekeeper'):
            articles = Article.objects.all().select_related('client').prefetch_related('products')
        else:
            articles = []
        
        return render(request, self.template_name, {'articles': articles, 'form': form})
class NotifyCourierView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/notify_courier.html'
    
    def test_func(self):
        return self.request.user.is_storekeeper

    def get(self, request, *args, **kwargs):
        form = NotificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = NotificationForm(request.POST, user=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user  # Set the sender as the logged-in user
            notification.receiver = form.cleaned_data['receiver']
            notification.save()
            return redirect('notify_courier')
  
class AddArticlesView(View):
    template_name = 'dms/add_article.html'

    def get(self, request, *args, **kwargs):
        form = ArticleForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.client = Client.objects.get(user=request.user)
            article.save()

            # Process dynamic product fields
            products = []
            index = 0
            while True:
                name = request.POST.get(f'product_name_{index}')
                description = request.POST.get(f'product_description_{index}')
                price = request.POST.get(f'product_price_{index}')
                category = request.POST.get(f'product_category_{index}')
                image = request.FILES.get(f'product_image_{index}')
                
                if not name or not description:
                    break
                
                # Create or update the product in the database
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': description,
                        'price': price,
                        'category': category,
                        'image': image,
                    }
                )
                products.append(product)
                index += 1

            article.products.set(products)  # Assign products to the article
            notify_courier(article)  # Notify couriers
            
            # Redirect to manage articles page with context
            return redirect('manage_articles')

        return render(request, self.template_name, {'form': form})               
class ManageRefundsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/manage_refunds.html'
    
    def test_func(self):
        return self.request.user.is_storekeeper

    def get(self, request, *args, **kwargs):
        refunds = Refund.objects.all()
        form = RefundForm()
        return render(request, self.template_name, {'refunds': refunds, 'form': form})

    def post(self, request, *args, **kwargs):
        form = RefundForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_refunds')
        refunds = Refund.objects.all()
        return render(request, self.template_name, {'refunds': refunds, 'form': form})
class ManageDeliveriesView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/manage_deliveries.html'
    
    def test_func(self):
        return self.request.user.is_courier

    def get(self, request, *args, **kwargs):
        courier = Courier.objects.get(user=request.user)
        deliveries = Delivery.objects.filter(courier=courier)
        notifications = Notification.objects.filter(sender=request.user)
        form = DeliveryForm()
        return render(request, self.template_name, {'deliveries': deliveries, 'form': form, 'notifications': notifications})

    def post(self, request, *args, **kwargs):
        delivery_id = request.POST.get('delivery_id')
        delivery = get_object_or_404(Delivery, id=delivery_id, courier__user=request.user)
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            return redirect('manage_deliveries')
        courier = get_object_or_404(Courier, user=request.user)
        deliveries = Delivery.objects.filter(courier=courier)
        notifications = Notification.objects.filter(user=request.user)
        return render(request, self.template_name, {'deliveries': deliveries, 'form': form, 'notifications': notifications})
    
class ViewDeliveriesView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/view_deliveries.html'

    def test_func(self):
        return self.request.user.is_courier

    def get(self, request, *args, **kwargs):
        courier = Courier.objects.get(user=request.user)
        deliveries = Delivery.objects.filter(courier=courier)
        return render(request, self.template_name, {'deliveries': deliveries})

    def post(self, request, *args, **kwargs):
            delivery_id = request.POST.get('delivery_id')
            delivery = get_object_or_404(Delivery, id=delivery_id, courier__user=request.user)
            form = DeliveryForm(request.POST, instance=delivery)
            if form.is_valid():
                form.save()
                return redirect('manage_deliveries')
            courier = get_object_or_404(Courier, user=request.user)
            deliveries = Delivery.objects.filter(courier=courier)
            return render(request, self.template_name, {'deliveries': deliveries, 'form': form})    
@method_decorator(login_required, name='dispatch')
class MakeOrderView(View):
    template_name = 'dms/make_order.html'

    def get(self, request):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return redirect('complete_profile')  # Redirect to a profile completion page
        cart_items = Cart.objects.filter(client=client)
        return render(request, self.template_name, {'cart_items': cart_items})

    def post(self, request):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return redirect('complete_profile')  # Redirect to a profile completion page
        cart_items = Cart.objects.filter(client=client)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        delivery_address = request.POST['delivery_address']

        order = Order.objects.create(
            client=client,
            total_price=total_price,
            delivery_address=delivery_address,
            payment_status='Pending',
            delivery_status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        cart_items.delete()
        return redirect('home')
    
class ViewOrdersView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/dashboards/views_orders.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'client')

    def get(self, request, *args, **kwargs):
        client = request.user.client
        orders = Order.objects.filter(client=client)
        return render(request, self.template_name, {'orders': orders})
    
class DeclineOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/decline_order.html'
    
    def test_func(self):
        return self.request.user.is_client

    def get(self, request, *args, **kwargs):
        form = OrderForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_orders')
        return render(request, self.template_name, {'form': form})

class ViewCartView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/view_cart.html'
    
    def test_func(self):
        return self.request.user.is_client

    def get(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(client=request.user)
        return render(request, self.template_name, {'cart_items': cart_items})

class AddToCartView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'dms/add_to_cart.html'
    
    def test_func(self):
        return self.request.user.is_client

    def get(self, request, *args, **kwargs):
        form = OrderForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_cart')
        return render(request, self.template_name, {'form': form})
   
class CourierHomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'dms/dashboards/courier_home.html'
    permission_required = ('DMS.can_view_deliveries', 'DMS.can_manage_deliveries')

    def handle_no_permission(self):
        return redirect('login')
    
class ClientHomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'dms/home.html'
    permission_required = ('DMS.can_make_orders', 'DMS.can_view_cart')

    def handle_no_permission(self):
        return redirect('login')

class StorekeeperHomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'dms/dashboards/storekeeper_home.html'
    permission_required = ('DMS.can_manage_articles', 'DMS.can_notify_courier')

    def handle_no_permission(self):
        return redirect('login')

class AdminHomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'dms/dashboards/admin_home.html'
    permission_required = ('DMS.can_view_overall_info',)

    def handle_no_permission(self):
        return redirect('login')

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'dms/signup_form.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_client = True
        user.save()
        client_group = Group.objects.get(name='Clients')
        user.groups.add(client_group)
        Client.objects.create(user=user, phone_number=user.phone_number)
        return super().form_valid(form)    
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dms/home.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().get(request, *args, **kwargs)

class CustomLogoutView(View):
    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse_lazy('login'))

@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin:user_changelist')
    else:
        form = AdminUserCreationForm()
    return render(request, 'dms/dashboards/admin_form.html', {'form': form})
# def admin_form(request):
#     form = AdminUserCreationForm()
#     return render(request, 'dms/dashboards/admin_form.html', {'form': form})

def view_overall_info(request):
    context = {
        'total_users': User.objects.count(),
        'total_clients': Client.objects.count(),
        'total_couriers': Courier.objects.count(),
        'total_storekeepers': Storekeeper.objects.count(),
        'total_products': Product.objects.count(),
        'total_articles': Article.objects.count(),
        'total_orders': Order.objects.count(),
        'total_deliveries': Delivery.objects.count(),
        'total_notifications': Notification.objects.count(),
        'total_reviews': Review.objects.count(),
    }
    return render(request, 'admin_home.html', context)

def register(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in
            # Redirect based on the user's role
            if user.is_client:
                return redirect('client_home')
            elif user.is_courier:
                return redirect('courier_home')
            elif user.is_storekeeper:
                return redirect('storekeeper_home')
            else:
                return redirect('home')  
    else:
        form = AdminUserCreationForm()
    return render(request, 'dms/dashboards/admin_form.html', {'form': form})

@login_required
def courier_home(request):
    if not request.user.is_courier:
        return redirect('home')

    courier = Courier.objects.get(user=request.user)
    notifications = Notification.objects.filter(receiver=courier, read=False)
    pending_orders = Order.objects.filter(delivery_status='Pending').select_related('client')
    for order in pending_orders:
        print(f"Order ID: {order.id}, Client Username: {order.client.user.username}, Address: {order.delivery_address}, Created At: {order.created_at}")

    context = {
        'notifications': notifications,
        'pending_orders': pending_orders,
        'courier': courier
    }
    return render(request, 'courier_home.html', context)

@login_required
def notification_page(request):
    if not request.user.is_courier:
        return redirect('home')

    courier = Courier.objects.get(user=request.user)
    unread_notifications = Notification.objects.filter(receiver=courier, read=False)
    pending_orders = Order.objects.filter(delivery_status='Pending').select_related('client')
    print('Unread notifications:', unread_notifications)
    print('Pending orders:', pending_orders)
    context = {
        'unread_notifications': unread_notifications,
        'pending_orders': pending_orders,
        'courier': courier
    }
    return render(request, 'dms/dashboards/notification_page.html', context)

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.read = True
    notification.save()
    return redirect('notification_page')

def deliver_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        # Update the order status to delivered
        order.delivery_status = 'Delivering...'
        order.save()
        return redirect('notification_page')
    else:
        return redirect('notification_page')
class CustomLoginView(LoginView):
    template_name = 'DMS/login.html'

    def get_success_url(self):
        user = self.request.user
        print(f"User role: client={user.is_client}, courier={user.is_courier}, storekeeper={user.is_storekeeper}, admin={user.is_admin}")
        if user.is_authenticated:
            if user.is_client:
                return reverse_lazy('client_home')  # Redirect to client home
            elif user.is_courier:
                return reverse_lazy('courier_home')  # Redirect to courier home
            elif user.is_storekeeper:
                return reverse_lazy('storekeeper_home')  # Redirect to storekeeper home
            elif user.is_admin:
                return reverse_lazy('admin_home')  # Redirect to admin home
        return super().get_success_url()
    def form_valid(self, form):
        # Log the user in
        response = super().form_valid(form)
        # Redirect to the appropriate URL
        return redirect(self.get_success_url())
      
# def courier_home(request):
#     return render(request, 'dms/dashboards/courier_home.html')

# def storekeeper_home(request):
#     return render(request, 'dms/dashboards/storekeeper_home.html')

# def admin_home(request):
#     return render(request, 'dms/dashboards/admin_home.html')
# def LoginView(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             # Obtain token
#             response = requests.post(f'{settings.API_URL}/api/token/', data={'username': username, 'password': password})
#             if response.status_code == 200:
#                 request.session['token'] = response.json()['access']
#                 return redirect('product-list')
#     return render(request, 'dms/login.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'dms/product_list.html', {'products': products})




#REST APIs
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

class CourierViewSet(viewsets.ModelViewSet):
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]

class StorekeeperViewSet(viewsets.ModelViewSet):
    queryset = Storekeeper.objects.all()
    serializer_class = StorekeeperSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
