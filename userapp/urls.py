from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from wallet.views import wallet as WalletView
from wallet.views import paymenthandler2 as paymenthandlerView

app_name = 'user_app'

urlpatterns = [
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('',views.home,name='home'),
    path('signup/',views.user_signup,name='signup'),
    path('verify/',views.verify_otp,name='verify_otp'),
    #path('resendotp/',views.resend_otp,name='resend_otp'),
    path('forgotpassword/', views.forgotpassword, name='forgot_password'),
    path('resetpassword/<uidb64>/<token>/',views.resetpassword,name='reset_password'),
    path('resetpassword/',views.reset_password,name='reset_password'),
    
    #user profile
    path('myaccountmanager/',views.myaccountmanager,name='my_account_manager'),
    path('accountdetails/',views.accountdetails,name='account_details'),
    path('editprofile/',views.editprofile,name='edit_profile'),
    path('wallet/',WalletView, name='wallet'),
    path('paymenthandler2/',paymenthandlerView,name='paymenthandler2'),


    path('addressbook/',views.addressbook,name='address_book'),
    path('addaddress/', views.addaddress, name='add_address'),
    path('editaddress/<int:pk>', views.editaddress, name='edit_address'),
    path('deleteaddress/<int:pk>', views.deleteaddress, name='delete_address'),
    path('defaultaddress/<int:pk>', views.defaultaddress, name='default_address'),
    
    path('myorders', views.myorders, name='my_orders'),
    path('cancelorder', views.cancel_order, name='cancel_order'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

