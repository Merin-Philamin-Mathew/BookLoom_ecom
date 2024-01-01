from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'admin_app'

urlpatterns = [
    path('dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout')
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

