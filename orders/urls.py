from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'order_app'

urlpatterns = [
    path('place-order/<int:address_id>/', views.place_order, name="place_order"),
    #path('payment/',views.payment,name="payment"),
    path('order-success/',views.order_success,name="order_success"),
    path('download_invoice/<str:order_id>/', views.download_invoice, name='download_invoice'),
    path('payment-handler/',views.paymenthandler,name="payment_handler"),
    path('payment-failed/<str:order_id>/',views.payment_failed,name="payment_failed"),
    path('apply-wallet/<str:order_id>',views.apply_wallet,name="apply_wallet"),
    path('apply-coupon/',views.apply_coupon,name="apply_coupon"),
    path('clear-coupon/',views.clear_coupon,name="clear_coupon"),
    # path('test/',views.test,name="test"),
]