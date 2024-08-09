from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
     ManageArticlesView,register,LoadQuartersView ,notification_page, mark_as_read, deliver_order,view_cart ,NotifyCourierView, ManageRefundsView,
    ViewDeliveriesView, ManageDeliveriesView,AddArticlesView,
    MakeOrderView, ViewOrdersView, ManageCartView,
    UserViewSet, ClientViewSet, CourierViewSet, StorekeeperViewSet, 
    ProductViewSet, ArticleViewSet, OrderViewSet, DeliveryViewSet, 
    NotificationViewSet, OrderConfirmationView,ReviewViewSet,ProductDetailView, add_to_cart, product_list, SignUpView, HomeView, CustomLogoutView, CustomLoginView, CourierHomeView, StorekeeperHomeView, AdminHomeView,ClientHomeView,
)
app_name = 'dms'
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'couriers', CourierViewSet)
router.register(r'storekeepers', StorekeeperViewSet)
router.register(r'products', ProductViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'deliveries', DeliveryViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    # path('admin_form/', admin_form, name='adminform'),
    path('view_overall/', register, name='admin_form'),
    path('notification_page/', notification_page, name='notification_page'),
    path('mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('add-articles/', AddArticlesView.as_view(), name='add_articles'),
    path('register/', register, name='admin_form'),
    path('home/', HomeView.as_view(), name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(template_name='dms/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('products/', product_list, name='product_list'),
    # path('client-home/', client_home, name='client_home'),
    path('order-confirmation/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('client-home/', ClientHomeView.as_view(), name='client_home'),
    path('courier-home/', CourierHomeView.as_view(), name='courier_home'),
    path('storekeeper-home/', StorekeeperHomeView.as_view(), name='storekeeper_home'),
    path('admin-home/', AdminHomeView.as_view(), name='admin_home'),
     path('manage-articles/', ManageArticlesView.as_view(), name='manage_articles'),
    path('notify-courier/', NotifyCourierView.as_view(), name='notify_courier'),
    path('manage-refunds/', ManageRefundsView.as_view(), name='manage_refunds'),
    path('view-deliveries/', ViewDeliveriesView.as_view(), name='view_deliveries'),
    path('cart/', view_cart, name='cart'),
    path('manage-deliveries/', ManageDeliveriesView.as_view(), name='manage_deliveries'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('view-orders/', ViewOrdersView.as_view(), name='view_orders'),
    path('manage-cart/', ManageCartView.as_view(), name='view_cart'),
     path('deliver_order/<int:order_id>/', deliver_order, name='deliver_order'),
    path('api/', include(router.urls)),
    path('load-quarters/', LoadQuartersView.as_view(), name='load_quarters'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)