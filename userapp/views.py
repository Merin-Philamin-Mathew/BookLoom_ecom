from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from adminapp.models import NewUser
from .forms import UserRegisterForm
from django.http import HttpResponseRedirect
""" from django.conf import settings


NewUser = settings.AUTH_USER_MODEL """

# Create your views here.
def home(request):
    return render(request, 'user_template\home.html')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('user_app:login')


def user_signup(request):
    if request.user.is_authenticated:    
        return redirect('user_app:home')
    
    if request.method == 'POST':
       form = UserRegisterForm(request.POST or None)

    #    if form.exists():
    #        messages.warning(request, 'Email is already taken.')
    #        return HttpResponseRedirect(request.path_info)
       if form.is_valid():
           user = form.save()
           messages.success(request, 'An email has been sent on your mail.')
           return HttpResponseRedirect(request.path_info)

        #    username = form.cleaned_data.get("username")
        #    messages.success(request, f"Hey {username}, Your account created successfully")
        #    user = authenticate(username = form.cleaned_data['email'],
        #                        password = form.cleaned_data['password1']
        #                        )
        #    login(request, user)
        #    return redirect('user_app:home')

    form = UserRegisterForm()
    context = {
        'form':form,
    }
    return render(request, "user_template/signup.html",context)



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




