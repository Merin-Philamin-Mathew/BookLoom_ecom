from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages
from store.models import Product, ProductVariant
from . models import Cart, CartItem
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse,HttpResponse

from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from userapp.forms import UserRegisterForm,AddressForm
from adminapp.models import Addresses

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def cart(request, total=0, quantity=0, cart_items = None):
    try:
        print("cart/cart/entered try")
        tax=0
        grand_total = 0
        discount = 0
        if request.user.is_authenticated:
            print("cart/cart/user is authenticated")
            cart_items = CartItem.objects.filter(user=request.user, is_stock=True)
           
        else:
            print("cart/cart/user is not authenticated")
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_stock=True)
        
        print("cart/cart/item",cart_items)
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
            discount += (cart_item.product.discount())*(cart_item.quantity)

        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'discount':discount
    }

    return render(request, 'user_template/cart-order-payment/cart.html', context)

def add_cart(request, product_id):
    print("cart/entered to add_cart")
    product = ProductVariant.objects.get(id=product_id) 
    current_user = request.user
    if current_user.is_authenticated:
        try:
            print("cart/add_cart,authenticated,cartitem increasing quantity")
            cart_item = CartItem.objects.get(product = product, user = current_user)
            cart_item.quantity += 1 #cart_item.quantity = cart_item.quantity+1
            if cart_item.product.stock < cart_item.quantity:
                cart_item.quantity -= 1
                messages.warning(request, "Sorry, product stock limit exceeded.")
                return redirect('cart_app:cart')
            cart_item.save()
        except CartItem.DoesNotExist:
            print("cart/add_cart,authenticated,cartitem adding for first time")
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
                #user = request.user if isinstance(request.user, NewUser) else None
            )
            cart_item.save()
    else:
        try:
            print("cart/add_cart,not authenticated,cart retrieving")
            cart = Cart.objects.get(cart_id = _cart_id(request))#get the cart using the cart_id present
            print("cart/cart", cart, cart.cart_id)
        except Cart.DoesNotExist:
            print("cart/add_cart,not authenticated,cart adding for first time")
            cart = Cart.objects.create(
                cart_id = _cart_id(request),
            )
            print("cart/add_cart/new session",cart.cart_id)
        cart.save()

        try:
            print("cart/add_cart,not authenticated,cartitem adding for first time")
            cart_item = CartItem.objects.get(product = product, cart = cart)
            if cart_item.product.stock == 0:
                messages.warning(request, "Sorry, the product is out of stock.")
                return redirect('cart_app:cart')
            cart_item.quantity += 1 #cart_item.quantity = cart_item.quantity+1
            cart_item.save()
        except CartItem.DoesNotExist:
            print("cart/add_cart,not authenticated,cartitem adding for first time")
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
                #user = request.user if isinstance(request.user, NewUser) else None
            )
            cart_item.save()
    return redirect('cart_app:cart')


def remove_cart(request, product_id):
    product = get_object_or_404(ProductVariant,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart_app:cart')

def remove_cart_item(request, product_id):
    product = get_object_or_404(ProductVariant, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = product, cart=cart)
    cart_item.delete()
    return redirect('cart_app:cart')

@login_required(login_url='userapp_app:login')
def delivery_address(request):
    print('cart/delivery_address')
    current_user = request.user
    form = AddressForm(user=current_user)
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    # if request.method == 'POST':
    #     print('cart/delivery_address/post')
    #     return redirect('order_app:place_order')
      
    context = {
        'form' : form,
        'addresses' : addresses, 
    }
    return render(request, 'user_template/cart-order-payment/delivery-address.html', context)




@login_required(login_url='userapp_app:login')
def checkout(request, total=0, quantity=0, cart_items = None):
    try:
        tax=0
        grand_total = 0
        if request.user.is_authenticated:
            print("cart/checkout/user is authenticated")
            cart_items = CartItem.objects.filter(user=request.user, is_stock=True)
        else:
            print("cart/checkout/user is not authenticated")
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_stock=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    addresses = Addresses.objects.filter(user=request.user, is_active=True).order_by('-is_default')
    form = AddressForm(user=request.user)
    context = {
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'form':form,
        'addresses' : addresses, 
    }
    return render(request, 'user_template/cart-order-payment/checkout.html',context)


