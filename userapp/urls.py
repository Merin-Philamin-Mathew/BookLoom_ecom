from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user_app'

urlpatterns = [
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('home',views.home,name='home'),
    path('signup/',views.user_signup,name='signup'),
    path('verify/',views.verify_otp,name='verify_otp'),
    path('product_view/<pk>',views.product_view,name='product_view')
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

