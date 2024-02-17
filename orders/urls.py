from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'order_app'

urlpatterns = [
    path('place-order/<int:address_id>/', views.place_order, name="place_order"),
    #path('payment/',views.payment,name="payment"),
    path('order-success/',views.order_success,name="order_success"),
    path('payment-handler/',views.paymenthandler,name="payment_handler"),
    # path('test/',views.test,name="test"),
]