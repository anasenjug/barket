from xml.etree.ElementInclude import include
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
from .forms import LoginForm



app_name = "app"
urlpatterns = [
    path('', views.index, name="index"),
    path('products/', views.products, name="products"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.CustomLoginView.as_view(redirect_authenticated_user=True, template_name='core/login.html',
                                           authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.success, name='success'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('about/', views.about, name='about'),
    path('top_up/', views.top_up, name='top_up'),
    path('top_ups/', views.top_ups, name='top_ups'),
    path('top-ups-admin/', views.top_ups_admin, name='top_ups_admin'),
]