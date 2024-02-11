from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store_app'

urlpatterns = [
     path('',views.viewstore,name='view_store'),
     path('<slug:category_slug>/',views.viewstore,name='products_by_category'),
     path('ajax/add-to-cart/', views.add_to_cart, name='add_to_cart'),
     path('<slug:category_slug>/<slug:product_variant_slug>/',views.product_detail,name='product_detail'),


]