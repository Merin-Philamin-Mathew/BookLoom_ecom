from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cart_app'

urlpatterns = [
    path('cart/',views.cart,name="cart"),
    path('add-cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('remove-cart/<int:product_id>/',views.remove_cart,name="remove_cart"),
    path('remove-cart-item/<int:product_id>/',views.remove_cart_item,name="remove_cart_item"),
    
    path('checkout/',views.checkout,name="checkout"),
]