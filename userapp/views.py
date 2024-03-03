
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

from cart.models import Cart, CartItem
from cart.views import _cart_id

import requests

""" from django.conf import settings


NewUser = settings.AUTH_USER_MODEL """

@never_cache
def home(request):
    print(request.user)
    products = ProductVariant.objects.all().filter(is_active = True)
    newproducts = ProductVariant.objects.all().filter(is_active= True).order_by("-id")
    authors = Author.objects.all().filter(is_active=True)
    context = {
        'products':products,
        'newproducts':newproducts, 
        'authors':authors,
    }
    return render(request, 'user_template\home.html', context)

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
                    print(cart_item)
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
                return redirect('user_app:user_sign')
            request.session['registration_form_data']=form.cleaned_data
            otp = random.randint(100000,999999) 
            request.session['otp']=str(otp)
            expiration_time = timezone.now() + timedelta(minutes=1)
            request.session['otp_expiry_time'] = expiration_time.isoformat()  # Expires after 1 minute
            send_mail(
                'BookLoom OTP Verification',
                'Your OTP is '+str(otp),
                'merinphilaminmathew19@gmail.com',
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
        print("otp...............", request.session.get('otp'))
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
                    print(form_data, 'user created')
                    user.save()

                    # Authenticate and log in the user
                    authenticated_user = authenticate(request, username=email, password=raw_password)
                    print(f'Authenticated user: {authenticated_user}')
                    if authenticated_user:
                        login(request, authenticated_user)
                        print(f'Request user: {request.user}')

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
        # country = Country.objects.all()
        # states = State.objects.all()
        # addressform = AddressBookForm()
        # orders = Order.objects.filter(user = request.user).exclude(status="New").order_by('-created_at')
        
        context = {
            'user' : user, 
            # 'states' : states,
            # 'country' : country,
            # 'addressform' : addressform, 
            # 'orders' : orders,   
        }
            
        #context.update(catcom(request))
        try:              #comparing two objects here not fields
            if Profile.objects.filter(user = user).exists:
                profile = Profile.objects.get(user = user)
                context['profile'] = profile
        except:
            pass
        
        # try:
        #     if AddressBook.objects.filter(user = user).exists:
        #         address = AddressBook.objects.filter(user = user)
        #         context['address'] = address
        # except:
        #     pass
        # try:
        #     if AddressBook.objects.filter(user = user , default = True).exists:
        #         d_address = AddressBook.objects.get(user = user ,default = True)
        #         context['d_address'] = d_address
        # except:
        #     pass
        
      
        return render(request, 'profile/dashboard.html')
    
    return redirect('user_app:login')

@login_required(login_url='userapp_app:login')
def accountdetails(request):
    current_user = request.user
    user = NewUser.objects.get(username = current_user.username)
    context = {
        'user':user
        }
    #context.update(catcom(request))
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
            return render(request, 'profile\edit-profile.html',context)
    return render(request, 'profile\edit-profile.html',{'form':form})
   
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
            print(error)
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
        #address = Addresses(user = user)
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
            print(error)
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
         
""" 
def update_address(request):

    if request.method == 'GET':
        id = request.GET.get('id')
        try:
            address = Addresses.objects.get(id = int(id))
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': 'Address not found'
            })
        
        address_form = AddressForm(request.POST, instance = address)
        form_data = model_to_dict(address_form.instance)
        form_data.pop('country')
        form_data['country'] = address.country.name
        print(form_data)

        country_choices = get_country_choices()
        countries = json.dumps(country_choices)
        
        return JsonResponse({
            'formData': form_data,
            'countries': countries
        })
    
        # return JsonResponse({
        #     'id': address.id,
        #     'name': address.name,
        #     'phone_number':address.phone_number,
        #     'addrl1': address.address_line_1,
        #     'addrl2': address.address_line_2,
        #     'city': address.city,
        #     'state': address.state,
        #     'country': address.get_country_display(),
        #     'pincode': address.pincode,
        # })
    elif request.method =='POST':
        
        address_id = request.POST.get('id')
        try:
            address = Addresses.objects.get(id = address_id)
            print(address)
        except Exception as e:
            print(e)

        address_form = AddressForm(request.POST,instance = address)
        if address_form.is_valid():
            new_address = address_form.save()

            return JsonResponse({
                "status" : 'Success',
                'message': 'Address updated successfully'
            })
        else:
            return JsonResponse({
                "name_error": address_form.errors
                })    

   
            
              
  """   


###################### ORDER MANAGEMENT #######################
@login_required(login_url='userapp_app:login')
def myorders(request):
    current_user = request.user
    all_orders = Order.objects.filter(user=current_user, is_ordered=True)
    all_products = OrderProduct.objects.filter(user=current_user, ordered=True)
    
    context = {
        'all_orders' : all_orders,
        'all_products' : all_products,
    }
    return render(request, 'profile/my-orders.html',context)

""" def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    payment = Payment.objects.all()
    for i in payment:
        print(i.payment_order_id)
        print(i.payment_id,i.payment_method)
   
    status = Order.ORDER_STATUS_CHOICES



    context = {
        'order': order,
        'order_products': order_products,
        'status': status,
    }
    return render(request, 'admin_templates/order_details.html', context)
    
 """

#################### CANCEL ORDER ########################
def cancel_order(request):
    print("user_app/cancel_order")
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
                product.quantity = 0
                product.save() 
        order.order_status = 'Cancelled'
        order.save()
        if order.payment.payment_method == 'Razor-pay':
            amount = order.order_total
            wallet=Wallet.objects.get(user=request.user)
            wallet.balance+=amount
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
                    product.quantity = 0
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
    print(order.order_status)
    return redirect('user_app:my_orders')    

################### RETURN ORDER #################
# def return_order(request):
#     order_id = request.GET.get('order_id')
#     order = Order.objects.get(id=order_id,user=request.user)
#     if order.created_at



  


def update_password(request):  
    print("userapp/update_password")
    if request.method == 'POST':
        print("userapp/update_password/post")
        try:
            print("userapp/update_password/post/try")
            user = request.user
            user = NewUser.objects.get(id = user.id)
        except:
            print("userapp/update_password/post/except")
            pass
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        print(new_password)
        if user and check_password(old_password, user.password):
            print("userapp/update_password/post/user and check_password(old_password, user.password)")
            user.password = make_password(new_password)
            user.save()
            print(user.password)
            return JsonResponse({'message': 'Password update successful'})
        else:
            print("userapp/update_password/post/not equal")
            print(user.password)
            return HttpResponseBadRequest('Invalid credentials')
    context = {}
    return render(request , 'profile/changepass.html',context)



""" def user_signup(request):
    # if request.user.is_authenticated:    
    #     return redirect(home)
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if NewUser.objects.filter(username=username):
                messages.add_message(request,messages.WARNING, "!!! Username Already Exist !!!")
                print("!!! Username Already Exist !!!")
            elif NewUser.objects.filter(email=email):
                messages.add_message(request,messages.WARNING, "!!! Email Already exist !!!")
                print("!!! Email Already exist !!!")
            else:
                password = make_password(password, salt=None, hasher="pbkdf2_sha256")
                user = NewUser(username=username, email=email, password=password)
                user.save()
                user = authenticate(request ,username=email, password=password2)
                login(request, user)
                messages.success(request, f'hey {username}, your account has created succesfully')
                return redirect('user_app:home')          
        else:
            print("password not matching")
            messages.add_message(request,messages.WARNING,"!!! Password not matching !!!") 
                
    return render(request, 'user_template\signup.html') """




