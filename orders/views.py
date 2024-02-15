from django.shortcuts import render
from cart.models import CartItem, Cart
from .models import Order, OrderProduct, Payment
from django.shortcuts import render, get_object_or_404, redirect
from userapp.forms import AddressForm
from django.http import HttpResponse
from datetime import datetime as dt

def order_success(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    tax = 0
    grand_total = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.sale_price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    # Set your payment ID here
    custom_datetime = dt.now()  # Use a different variable name
    payment = Payment.objects.create(
        user=current_user,
        payment_id=f'COD-{current_user.pk:05d}-{custom_datetime.strftime("%Y%m%d%H%M%S")}',
        payment_method='Cash on Delivery',
        amount_paid=grand_total,
        status='Processed',
    )

    # Get the existing order (you may need to adjust this query)
    orders = Order.objects.filter(user=current_user)

# Check if there is exactly one order matching the conditions
    if orders.count() == 1:
        order = orders.first()
    else:
    # Handle the case where multiple or no orders are found
    # You may raise an exception, redirect the user, or handle it based on your requirements
    # For now, I'll raise an exception
        raise ValueError("Expected one order, but found multiple or none.")
    # Associate the payment with the existing order
    order.payment = payment
    order.save()

    # Save ordered products
    for cart_item in cart_items:
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.sale_price,
            ordered=True
        )
        order_product.save()

    # Mark the order as ordered
    order.is_ordered = True
    order.save()

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'payment_method': 'Cash on delivery'
    }

    # Clear the user's cart after placing the order
    cart_items.delete()
    return render(request, 'user_template/cart-order-payment/order-success.html', context)
 
import datetime
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store_app:view_store')
    tax=0
    grand_total = 0
    for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
    tax = (2*total)/1001
    grand_total = total+tax

    if request.method == 'POST':
        form = AddressForm(request.user, request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            address = form.save(commit=False)
            address.is_default = True
            address.user = request.user  # Set the user before saving
            address.save()
            data.address = address
            #data.payment = request.POST['payment_method']
            data.order_note = request.POST['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #genarate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context= {
                 'order':order,
                 'cart_items':cart_items,
                 'total':total,
                 'tax':tax,
                 'grand_total':grand_total,
                 'payment_method':'Cash on delivery'
            }
            return render(request, 'user_template/cart-order-payment/payment.html', context)
    else:
        return redirect('cart_app:checkout')
    
def payment(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    tax = 0
    grand_total = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.sale_price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    # Set your payment ID here
    payment = Payment()
    payment.user=current_user,
    payment.payment_id=f'COD-{current_user.id:05d}-{datetime.now().strftime("%Y%m%d%H%M%S")}',  # Example: COD-00001-20220101120000
    payment.payment_method='Cash on Delivery',
    payment.amount_paid=grand_total,
    payment.status='Processed',  # Payment status will be updated upon delivery
    
    payment.save()

    # Get the existing order (you may need to adjust this query)
    order = Order.objects.get(user=current_user, is_ordered=False)

    # Associate the payment with the existing order
    order.payment = payment
    order.save()

    # Save ordered products
    for cart_item in cart_items:
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.sale_price,
            ordered=True
        )
        order_product.save()
        # Mark the order as ordered
        order.is_ordered = True
        order.save()
        context= {
                 'order':order,
                 'cart_items':cart_items,
                 'total':total,
                 'tax':tax,
                 'grand_total':grand_total,
                 'payment_method':'Cash on delivery'
            }

        # Update product stock or other relevant data as needed
        # cart_item.product.stock -= cart_item.quantity
        # cart_item.product.save()

    # Clear the user's cart after placing the order
    #cart_items.delete()

    return render(request, 'user_template/cart-order-payment/payment.html',context)
    





