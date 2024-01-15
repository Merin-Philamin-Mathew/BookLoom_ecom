from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from adminapp.models import NewUser
from .forms import UserRegisterForm
from django.http import HttpResponseRedirect
import random
from django.core.mail import send_mail
from store.models import Product
""" from django.conf import settings


NewUser = settings.AUTH_USER_MODEL """

# Create your views here.
def home(request):
    products = Product.objects.all().filter(is_available = True)
    newproducts = Product.objects.all().filter(is_available = True).order_by("-id")
    
    context = {
        'products':products,
        'newproducts':newproducts, 
    }
    return render(request, 'user_template\home.html', context)

def product_view(request,pk):
    #product_details = Product.objects.get(id=pk)
   
    return render(request, 'user_template\single_product_page.html')


def user_logout(request):
    if request.user.is_authenticated :
        logout(request)
    return redirect('user_app:login')


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
            send_mail(
                'BookLoom OTP Verification',
                'Your OTP is'+str(otp),
                'merinphilaminmathew19@gmail.com',
                [email],
                fail_silently=False,
            )

            return redirect('user_app:verify_otp')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, "user_template/signup.html", context)


def verify_otp(request):
    if 'otp' in request.session: 
        if request.method == 'POST':
            otp = request.POST.get('otp')
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
                messages.success(request, f'hey {username}, your account has created succesfully')
                return redirect('user_app:login')
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
        return render(request, "user_template/verify.html" )
    else:
        return redirect('user_app:signup')
    

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




