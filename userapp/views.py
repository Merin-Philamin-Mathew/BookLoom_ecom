
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from adminapp.models import NewUser
from .forms import UserRegisterForm
from django.http import HttpResponseRedirect
import random
from django.core.mail import send_mail
from store.models import Product, ProductVariant, Author
from datetime import timedelta, datetime
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
""" from django.conf import settings


NewUser = settings.AUTH_USER_MODEL """

@never_cache
def home(request):  
    products = ProductVariant.objects.all().filter(is_active = True)
    newproducts = ProductVariant.objects.all().filter(is_active= True).order_by("-id")
    authors = Author.objects.all().filter(is_active=True)
    context = {
        'products':products,
        'newproducts':newproducts, 
        'authors':authors,
    }
    return render(request, 'user_template\home.html', context)

def product_view(request,pk):
    #product_details = Product.objects.get(id=pk)
   
    return render(request, 'user_template\single_product_page.html')

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

@never_cache
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
                    password = form_data['password1']
                    password = make_password(password, salt=None, hasher="pbkdf2_sha256")
                    user = NewUser(username=username, email=email, phone_number=phone_number,password=password)
                    print(form_data,'user created')
                    user.save()
                    request.session.flush()
                    messages.success(request, f'Hey {username}, your account has created succesfully, Welcome to BookLoom')
                    return redirect('user_app:home')
                    # form = UserRegisterForm(form_data)
                    # if form.is_valid():
                    #     form.save()
                    #     messages.success(request, 'Registration Successful')
                    #     request.session['otp'].flush()
                    #     return redirect('user_app:login')
                    # else:
                    #     messages.error(request, 'Invalid form data')
                    #     return redirect('user_app:signup')
                else:
                    messages.error(request, 'Invalid otp')
                    return redirect('user_app:verify_otp')
            else:
                # request.session.flush('otp','otp_expiry_time')
                # messages.error(request, 'Time expired')
                return render(request, "user_template/verify.html" ,{'otp_expiry_time':otp_expiry_time})
                
        return render(request, "user_template/verify.html" )
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
   
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
        
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user is not None:
            username = user.username
            login(request, user)
            messages.success(request, f"Hey {username}, welcome back! You've logged in successfully.")
            return redirect('user_app:home') 
        else:
            # Check if the email exists in the user model
            if NewUser.objects.filter(email=email).exists():
                messages.warning(request, 'Invalid password')
            else:
                messages.warning(request, 'User does not exist')
       
    return render(request, 'user_template/login.html')


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
            messages.success(request, "sucessfully reset password")
            return render(request,'user_template/reset-success.html')

        else:
            messages.error(request, "Passwords are not match")
            return redirect('user_app:reset_password')
        
    else:
        return render(request, 'user_template/reset-password.html')


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




