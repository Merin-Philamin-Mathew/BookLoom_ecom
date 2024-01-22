from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user_app'

urlpatterns = [
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('home/',views.home,name='home'),
    path('signup/',views.user_signup,name='signup'),
    path('verify/',views.verify_otp,name='verify_otp'),
    #path('resendotp/',views.resend_otp,name='resend_otp'),
    path('forgotpassword/', views.forgotpassword, name='forgot_password'),
    path('resetpassword/<uidb64>/<token>/',views.resetpassword,name='reset_password'),
    path('resetpassword/',views.reset_password,name='reset_password'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

