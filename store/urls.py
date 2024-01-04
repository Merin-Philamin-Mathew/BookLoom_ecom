from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store_app'

urlpatterns = [
    path('category',views.listcategory,name='category'),
    path('editcategory/<pk>',views.editcategory,name='edit_category'),
    path('deletecategory/<pk>',views.deletecategory,name='delete_category'),
    path('listproducts',views.listproducts,name='list_products'),
    path('addproducts',views.addproducts,name='add_products'),
    path('editproducts/<pk>',views.editproducts,name='edit_products'),
    path('deleteproducts/<pk>',views.deleteproducts,name='delete_products'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

