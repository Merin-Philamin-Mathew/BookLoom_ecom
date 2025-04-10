
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from adminapp.models import NewUser
from .forms import UserRegisterForm,AddressForm
from django.http import HttpResponseRedirect
import random
from django.core.mail import send_mail
from store.models import Product, ProductVariant, Author
from adminapp.models import NewUser, Profile, Addresses
from orders.models import Order, OrderProduct, Payment
from wallet.models import Wallet, Transaction
from . forms import ProfileForm
from datetime import timedelta, datetime
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.http import JsonResponse,HttpResponseBadRequest
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from decimal import Decimal


from cart.models import Cart, CartItem
from cart.views import _cart_id

import requests

""" from django.conf import settings


NewUser = settings.AUTH_USER_MODEL """

@never_cache
def home(request):
    if 'referral_code' in request.session:
        del request.session['referral_code']
    products = ProductVariant.objects.all().filter(is_active = True)
    newproducts = ProductVariant.objects.all().filter(is_active= True).order_by("-id")
    authors = Author.objects.all().filter(is_active=True)
    context = {
        'products':products,
        'newproducts':newproducts, 
        'authors':authors,
    }
    return render(request, 'user_template/home.html', context)

#--------------user profile------------------
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
        
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart). exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            username = user.username
            login(request, user)
            messages.success(request, f"Hey {username}, welcome back! You've logged in successfully.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #next=/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                #{'next': '/checkout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('user_app:home') 
        else:
            # Check if the email exists in the user model
            if NewUser.objects.filter(email=email).exists():
                messages.warning(request, 'Invalid password')
            else:
                messages.warning(request, 'User does not exist')
       
    return render(request, 'user_template/login.html')

@never_cache
def user_logout(request):
    if request.user.is_authenticated :
        logout(request)
    return redirect('user_app:login')

@never_cache
def user_signup(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
    
        if form.is_valid():
            
            email = form.cleaned_data['email']
            check_user = NewUser.objects.filter(email=email).first()
            if check_user:
                messages.warning(request, "Email already exists")
                return redirect('user_app:signup')
            referral_code = request.POST.get('referral_code')
            if referral_code:
                check_referal = NewUser.objects.filter(refferal_code=referral_code).first()
                if not check_referal:
                    messages.warning(request, "There is no such referral code!")
                    return redirect('user_app:signup')
                request.session['referral_code']=referral_code

            request.session['registration_form_data']=form.cleaned_data
            otp = random.randint(100000,999999) 
            request.session['otp']=str(otp)
            expiration_time = timezone.now() + timedelta(minutes=1)
            request.session['otp_expiry_time'] = expiration_time.isoformat()  # Expires after 1 minute
            print('email going to sent')
            send_mail(
                'BookLoom OTP Verification',
                'Your OTP is '+str(otp),
                'hosthunt000@gmail.com',
                [email],
                fail_silently=False,
            )

            return redirect('user_app:verify_otp')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, "user_template/signup.html", context)

from django.db import transaction

@transaction.atomic
def verify_otp(request):
    if 'otp' in request.session: 
        if request.method == 'POST':
            otp = request.POST.get('otp')
            
            otp_expiry_time_str = request.session.get('otp_expiry_time')
            otp_expiry_time = datetime.fromisoformat(otp_expiry_time_str)

            if otp == request.session.get('otp') and timezone.now() <= otp_expiry_time:

                if otp == request.session.get('otp'):
                    form_data = request.session.get('registration_form_data')
                    username = form_data['username']
                    email = form_data['email']
                    phone_number = form_data['phone_number']
                    raw_password = form_data['password1']  # Get the raw password
                    password = make_password(raw_password, salt=None, hasher="pbkdf2_sha256")
                    user = NewUser(username=username, email=email, phone_number=phone_number, password=password)
                    user.save()
                    if 'referral_code' in request.session:
                        referral_user = NewUser.objects.filter(refferal_code=request.session['referral_code']).first()
                        wallet = Wallet.objects.get(user = referral_user)
                        wallet.balance += 100
                        wallet.save()
                        Transaction.objects.create(wallet=wallet, amount=100, transaction_type='REFERRAL')

                    # Authenticate and log in the user
                    authenticated_user = authenticate(request, username=email, password=raw_password)
                    if authenticated_user:
                        login(request, authenticated_user)
                        # providing referal_offer
                        messages.success(request, f'Hey {username}, your account has been created successfully. Welcome to BookLoom!')
                        return redirect('user_app:home')
                    else:
                        messages.error(request, 'Invalid authentication')
                        return redirect('user_app:verify_otp')
                else:
                    messages.error(request, 'Invalid otp')
                    return redirect('user_app:verify_otp')
            else:
                return render(request, "user_template/verify.html", {'otp_expiry_time': otp_expiry_time})
                
        return render(request, "user_template/verify.html")
    else:
        return redirect('user_app:signup')


    """ @never_cache
def resend_otp(request):
    if 'otp' in request.session:
        # Generate a new OTP
        new_otp = random.randint(100000, 999999)
        request.session['otp'] = str(new_otp)
        
        # Update the expiration time
        expiration_time = timezone.now() + timedelta(seconds=6)
        request.session['otp_expiry_time'] = expiration_time.isoformat()
        
        # Resend the email (you can reuse your existing code here)

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'No OTP in session'}) """
 

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if NewUser.objects.filter(email=email).exists():
            user = NewUser.objects.get(email__exact=email)

            current_site = get_current_site(request)
            subject = 'BookLoom : Reset your password'
            body = render_to_string('user_template/resetmailcontent.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, body, to=[to_email])
            send_email.send()
            messages.success(
                request, 'Password reset email has been sent to your email address')
            return render(request,'user_template/linksuccess.html')
        else:
            messages.error(request, "Account Does't Exists!!!")
            return redirect('user_app:forgot_password')
    return render(request, 'user_template/forgot-password.html')

def resetpassword(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = NewUser._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, NewUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.!')
        return redirect('user_app:reset_password')
    else:
        messages.error(request, 'Sorry, the activation link has expired.!')
        return redirect('user_app:login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['Confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = NewUser.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            #messages.success(request, "sucessfully reset password")
            return render(request,'user_template/reset-success.html')

        else:
            messages.error(request, "Passwords are not match")
            return redirect('user_app:reset_password')
        
    else:
        return render(request, 'user_template/reset-password.html')



@login_required(login_url='userapp_app:login')
def myaccountmanager(request):
    current_user = request.user
    if current_user.is_authenticated:
        user = NewUser.objects.get(username = current_user.username)
       
        context = {
            'user' : user,    
        }
        try:              #comparing two objects here not fields
            if Profile.objects.filter(user = user).exists:
                profile = Profile.objects.get(user = user)
                context['profile'] = profile
        except:
            pass
        return render(request, 'profile/dashboard.html')
    
    return redirect('user_app:login')

@login_required(login_url='userapp_app:login')
def accountdetails(request):
    current_user = request.user
    user = NewUser.objects.get(username = current_user.username)
    context = {
        'user':user
        }
    try:
        if Profile.objects.filter(user = user).exists:
            profile = Profile.objects.get(user = user)
            context['profile'] = profile
    except:
        pass
    return render(request , 'profile/account-details.html',context)
   
from django.db import transaction
@transaction.atomic
@login_required(login_url='userapp_app:login')
def editprofile(request):

    user = request.user
    try:
        profile=Profile.objects.get(user = user)
    except Profile.DoesNotExist as e :
        profile = Profile(user = user)
    form = ProfileForm(instance = profile)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile successfully completed!!.....")
            return redirect('user_app:account_details')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'profile/edit-profile.html',context)
    return render(request, 'profile/edit-profile.html',{'form':form})

###################### ADDRESS MANAGEMENT #######################

@login_required(login_url='userapp_app:login')
def addressbook(request):
    current_user = request.user
    address_form = AddressForm(user=current_user)
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    
    context = {
        'address_form' : address_form,
        'addresses' : addresses, 
    }
    return render(request, 'profile/address-book.html',context)

@login_required(login_url='userapp_app:login')
def addaddress(request):
    if request.method == 'POST':
        form = AddressForm(request.user, request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Set the user before saving
            address.save()
            messages.success(request, "Address successfully added!!.....")
            return redirect('user_app:address_book')
        else:
            error = form.errors
            context = {'form': form, 'error': error}
            return render(request, 'profile/add-address.html', context)
    
    form = AddressForm(user=request.user)
    return render(request, 'profile/add-address.html', {'form': form})
 
@login_required(login_url='userapp_app:login')
def editaddress(request,pk):
    user = request.user
    try:
        address=Addresses.objects.get(id = pk)
    except Addresses.DoesNotExist as e :
        pass

    if request.method == 'POST':
        form = AddressForm(request.user,request.POST,instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Set the user before saving
            address.save()
            messages.success(request, "Address successfully Updated!!.....")
            return redirect('user_app:address_book')
        else:
            error = form.errors
            context = {'form': form, 'error': error}
            return render(request, 'profile/edit-address.html', context)
    else:
        form = AddressForm(instance=address, user=user)
    return render(request, 'profile/edit-address.html', {'form': form})
 
@login_required(login_url='userapp_app:login')
def deleteaddress(request,pk):
    try:
        address = Addresses.objects.get(id=pk)
        address.is_active = False
        address.save()
        return redirect('user_app:address_book')                
    
    except Addresses.DoesNotExist:
        return redirect('user_app:address_book')   

@login_required(login_url='userapp_app:login')          
def defaultaddress(request, pk):
    try:  
        other = Addresses.objects.all().exclude(id=pk)
        for address in other:
            address.is_default = False
            address.save()

        address = Addresses.objects.get(id=pk)
        address.is_default = True
        address.save()
        return redirect('user_app:address_book')   
    except Addresses.DoesNotExist:
        return redirect('user_app:address_book')   
 
###################### ORDER MANAGEMENT #######################
@login_required(login_url='userapp_app:login')
def myorders(request):
    current_user = request.user
    all_orders = Order.objects.filter(user=current_user, is_ordered=True).order_by('-id')
    all_products = OrderProduct.objects.filter(user=current_user, ordered=True)
    
    context = {
        'all_orders' : all_orders,
        'all_products' : all_products,
    }
    return render(request, 'profile/my-orders.html',context)

def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    subtotal =0
    discount =0
    for item in ordered_products:
        subtotal += item.product_price*item.quantity
        discount += item.product.discount()*item.quantity
    discount += order.additional_discount

    context = {
        'order': order,
        'ordered_products': ordered_products,
        'subtotal':subtotal,
        'discount':discount
        # 'status': status,
    }
    return render(request, 'profile/order-detail.html', context)
    


#################### CANCEL ORDER ########################

def cancel_order(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id,user=request.user)
    orderproducts = OrderProduct.objects.filter(order=order,user=request.user)
    if order.order_status != 'Cancelled' and order.order_status != 'Delivered':
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            for product in order.ordered_products.all():
                # Add the canceled product quantity back to stock
                product.product.stock += product.quantity
                product.product.save()

                # Set the quantity of the canceled product to 0
                product.save() 
        order.order_status = 'Cancelled'
        order.save()
        if order.payment.payment_method == 'Razor-pay' or order.payment.payment_method == 'Wallet' :
            amount = order.order_total
            wallet=Wallet.objects.get(user=request.user)
            wallet.balance+=Decimal(amount)
            Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
            wallet.save()
            messages.success(request, f"your cancelled products amount, ₹{amount} has been credited to the wallet!")
            return redirect('user_app:wallet')  
    else:
        if order.order_status == 'Delivered':
             # Use a transaction to ensure atomicity
            with transaction.atomic():
                for product in order.ordered_products.all():
                    # Add the canceled product quantity back to stock
                    product.product.stock += product.quantity
                    product.product.save()

                    # Set the quantity of the canceled product to 0
                    product.save()
            messages.success(request, f"Order return initiated successfully , Our pickup team will be at the deliverd address shortly")
            order.order_status = 'Returned'
            order.save()
            if order.payment.payment_method == 'Razor-pay':
                """ amount = order.order_total
                wallet=Wallet.objects.get(user=request.user)
                wallet.balance+=amount
                Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
                wallet.save()
                messages.success(request, f"your returned products amount, ₹{amount} has been credited to the wallet!")
                return redirect('user_app:wallet') """ 
    order.save()       
    
    # if order.created_at < datetime.datetime.now() - datetime.timedelta(days=7):
    return redirect('user_app:my_orders')    

################### RETURN ORDER #################
# def return_order(request):
#     order_id = request.GET.get('order_id')
#     order = Order.objects.get(id=order_id,user=request.user)
#     if order.created_at


def update_password(request):  
    if request.method == 'POST':
        try:
            user = request.user
            user = NewUser.objects.get(id = user.id)
        except:
            pass
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        if user and check_password(old_password, user.password):
            user.password = make_password(new_password)
            user.save()
            return JsonResponse({'message': 'Password update successful'})
        else:
            return HttpResponseBadRequest('Invalid credentials')
    context = {}
    return render(request , 'profile/changepass.html',context)




