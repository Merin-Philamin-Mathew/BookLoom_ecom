from django.shortcuts import render
from cart.models import CartItem, Cart
from .models import Order, OrderProduct, Payment
from adminapp.models import Addresses
from django.shortcuts import render, get_object_or_404, redirect
from userapp.forms import AddressForm
from django.http import HttpResponse
from datetime import datetime as dt
from django.db import transaction

import razorpay
from django.http import JsonResponse,HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# By using the transaction.atomic decorator, you ensure that all database operations within the view are performed within a single transaction. 
# This helps maintain data consistency and prevents partial updates. 
# The cart items are deleted after rendering the order success page, allowing you to retrieve data from cart items before deletion
@transaction.atomic
def order_success(request, total=0, quantity=0):
    print('order/order_success')
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
    
    order = Order.objects.filter(user=current_user).last()
    if order.payment != None:
        payment = order.payment
    else:
        print("else part")
        payment = Payment.objects.create(
            payment_id=f'COD-{current_user.pk:05d}-{custom_datetime.strftime("%Y%m%d%H%M%S")}',
            payment_method='Cash on Delivery',
            amount_paid=grand_total,
            payment_status='PENDING',
        )
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

        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()

    # Mark the order as ordered

    order.is_ordered = True
    order.save()
    dummy_orders = Order.objects.filter(is_ordered = False)
    dummy_orders.delete()

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'payment':payment
    }

    # Clear the user's cart after placing the order
    cart_items.delete()
    return render(request, 'user_template/cart-order-payment/order-success.html', context)
 


import datetime
def place_order(request, address_id, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store_app:view_store')

    tax = 0
    grand_total = 0

    for cart_item in cart_items:
        total += (cart_item.product.sale_price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    # Common code for creating an order
    data = Order()
    data.user = current_user
    data.order_total = grand_total
    data.tax = tax
    data.ip = request.META.get('REMOTE_ADDR')

    razor_pay_key_id = 'rzp_test_fGwLaAdAhjOjbm'  # Use your Razorpay test key
    key_secret = '7qO0FhI7y3SZGPpikcUEvVf1'  # Use your Razorpay test secret key


    client = razorpay.Client(auth=(razor_pay_key_id, key_secret))
    amount = int(grand_total * 100)
    payment = client.order.create({'amount': amount, 'currency':'INR','payment_capture':1})
    data.razor_pay_order_id = payment['id']

    print('*********')
    print(payment)
    print('*********')
    if request.method == 'POST':
        form = AddressForm(request.user, request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.is_default = True
            address.user = request.user
            address.save()
            data.address = address
            data.order_note = request.POST['order_note']
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'payment':payment
            }
            return render(request, 'user_template/cart-order-payment/payment.html', context)

    elif address_id:
        address = Addresses.objects.get(user=current_user, id=address_id)
        address.is_default = True
        address.save()
        data.address = address
        data.save()
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'payment': payment
        }
        
        return render(request, 'user_template/cart-order-payment/payment.html', context)

    else:
        return redirect('cart_app:delivery_address')
    
    

@csrf_exempt
def paymenthandler(request):
    print("Payment Handler endpoint reached")
 
    # only accept POST request.
    if request.method == "POST":
        print("dsfsd")
        try:
            # Extract payment details from the POST request
            payment_id        = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature         = request.POST.get('razorpay_signature', '')
            amount         = request.GET.get('amount', '')
            
            print(f'1:{payment_id},2:{razorpay_order_id},3:{signature}')
            # Create a dictionary of payment parameters
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)

            if not result :
                print("mmmmmmmmmmm")
                # Payment signature verification failed
                # return render(request, 'paymentfail.html')
                return JsonResponse({'message': 'Payment signature verification failed'})
            else:
                print("lalalal")
                # Payment signature verification successful
                # Perform necessary actions after successful payment
                # Example: Capture payment, update database, etc.
                payment = Payment.objects.create(
                    payment_id=payment_id,
                    payment_method='Razor-pay',
                    amount_paid=amount,
                    payment_status='SUCCESS',
                )
                # payment = Payment.objects.get(payment_order_id=razorpay_order_id)
                # payment.status = 'SUCCESS'
                # payment.payment_id = payment_id
                # payment.payment_signature = signature
                payment.save()
                print("payment",payment)
                order = Order.objects.filter(razor_pay_order_id=razorpay_order_id).last()
                order.payment = payment
                order.save()
                print("order",order,"order.payment",order.payment)
                
                # Here you can add your logic to handle the payment and update your database accordingly
                
                return redirect('order_app:order_success')  # Redirect to success page
        except Exception as e:
            # Exception occurred during payment handling
            print('Exception:', str(e))
            return HttpResponseBadRequest()
    else:
        # Redirect to login page if request method is not POST
        return redirect('order_app:place_order')    
    






# def place_order(request, total=0, quantity=0):
#     print("order/place_order/")
#     current_user = request.user
#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('store_app:view_store')
#     tax=0
#     grand_total = 0
#     for cart_item in cart_items:
#             total += (cart_item.product.sale_price * cart_item.quantity)
#             quantity += cart_item.quantity
#     tax = (2*total)/1001
#     grand_total = total+tax

#     if request.method == 'POST':
#         form = AddressForm(request.user, request.POST)
#         if form.is_valid():
#             data = Order()
#             data.user = current_user
#             address = form.save(commit=False)
#             address.is_default = True
#             address.user = request.user  # Set the user before saving
#             address.save()
#             data.address = address
#             #data.payment = request.POST['payment_method']
#             data.order_note = request.POST['order_note']
#             data.order_total = grand_total
#             data.tax = tax
#             data.ip = request.META.get('REMOTE_ADDR')
#             data.save()
#             #genarate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             d = datetime.date(yr,mt,dt)
#             current_date = d.strftime("%Y%m%d")
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()
            
#             order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
#             context= {
#                  'order':order,
#                  'cart_items':cart_items,
#                  'total':total,
#                  'tax':tax,
#                  'grand_total':grand_total,
#                  'payment_method':'Cash on delivery'
#             }
#             return render(request, 'user_template/cart-order-payment/payment.html', context)
#     else:
#         return redirect('cart_app:checkout')
       

# def payment(request, total=0, quantity=0):
#     current_user = request.user
#     cart_items = CartItem.objects.filter(user=current_user)
#     tax = 0
#     grand_total = 0
    
#     for cart_item in cart_items:
#         total += (cart_item.product.sale_price * cart_item.quantity)
#         quantity += cart_item.quantity

#     tax = (2 * total) / 100
#     grand_total = total + tax

#     # Set your payment ID here
#     payment = Payment()
#     payment.user=current_user,
#     payment.payment_id=f'COD-{current_user.id:05d}-{datetime.now().strftime("%Y%m%d%H%M%S")}',  # Example: COD-00001-20220101120000
#     payment.payment_method='Cash on Delivery',
#     payment.amount_paid=grand_total,
#     payment.status='Processed',  # Payment status will be updated upon delivery
    
#     payment.save()

#     # Get the existing order (you may need to adjust this query)
#     order = Order.objects.get(user=current_user, is_ordered=False)

#     # Associate the payment with the existing order
#     order.payment = payment
#     order.save()

#     # Save ordered products
#     for cart_item in cart_items:
#         order_product = OrderProduct(
#             order=order,
#             payment=payment,
#             user=current_user,
#             product=cart_item.product,
#             quantity=cart_item.quantity,
#             product_price=cart_item.product.sale_price,
#             ordered=True
#         )
#         order_product.save()
#         # Mark the order as ordered
#         order.is_ordered = True
#         order.save()
#         context= {
#                  'order':order,
#                  'cart_items':cart_items,
#                  'total':total,
#                  'tax':tax,
#                  'grand_total':grand_total,
#             }

#         # Update product stock or other relevant data as needed
#         # cart_item.product.stock -= cart_item.quantity
#         # cart_item.product.save()

#     # Clear the user's cart after placing the order
#     cart_items.delete()

#     return render(request, 'user_template/cart-order-payment/review.html',context)
    





