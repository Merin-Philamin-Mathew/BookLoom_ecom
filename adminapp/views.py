from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from . models import NewUser

# Create your views here.

def admin_logout(request):
    if request.user.is_superuser:
        logout(request)
    return redirect('admin_app:admin_login')


def admin_login(request):
    if request.user.is_superuser:
            return redirect('admin_app:admin_dashboard')
        
    if request.method == 'POST':
        uname = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=uname, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_app:admin_dashboard') 
        # else:
        #     if User.objects.filter(username=uname):
        #         messages.add_message(request, messages.WARNING, 'Invaluser_id password')
        #     else:
        #         messages.add_message(request, messages.WARNING, 'Not admin')
    return render(request, 'admin_template/admin-login.html')


def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, 'admin_template\index.html')


def userinfo(request):
    users = NewUser.objects.all()

    context = {
        'users':users
    }
    return render(request, 'admin_template/user_management/all_user.html', context)

@login_required(login_url='admin_login')
def adduser(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            phone_number = request.POST['phone_number']
            password = request.POST['password']
            password = make_password(password, salt=None, hasher='pbkdf2_sha256')
            if NewUser.objects.filter(username=username):
                messages.add_message(request, messages.WARNING, 'username exist')
                return render(request, 'admin_template/user_management/add_user.html')
            elif NewUser.objects.filter(email=email):
                messages.add_message(request, messages.WARNING, 'email exist')
            elif NewUser.objects.filter(phone_number=phone_number):
                messages.add_message(request, messages.WARNING, 'phone number exist')
                return render(request, 'admin_template/user_management/add_user.html')
            else:
                user = NewUser(username=username, email=email, password=password, phone_number=phone_number)
                user.save()
            return redirect('admin_app:userinfo')
        return render(request, 'admin_template/user_management/add_user.html')
    
    return redirect('admin_app:userinfo')
    

def edituser(request,pk):
    if request.user.is_superuser:
        if request.method == "GET":
            if NewUser.objects.filter(user_id = pk):
                user = NewUser.objects.get(user_id = pk)
                context = {
                    'user_data':user
                }
                return render(request, 'admin_template/user_management/edit_user.html', context)
        elif request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            phone_number = request.POST['phone_number']
            status = request.POST['status']
            password = request.POST['password']
            password = make_password(password, salt=None, hasher="pbkdf2_sha256")
            if NewUser.objects.filter(user_id=pk):
                #checking the userdata before and after editing are not the same
                #befor saving the post form 
                #if any data of anyfield is same==changes are not done.
                #no need to go to that field again
                user = NewUser.objects.get(user_id=pk)
                if email and user.email != email:
                    if NewUser.objects.filter(email=email):
                        messages.add_message(request, messages.WARNING, 'email exist')
                        return render(request, 'admin_template/user_management/edit_user.html')
                    else:
                        user.email = email
                if username and user.username != username :
                    if NewUser.objects.filter(username=username):
                        messages.add_message(request, messages.WARNING, 'username exist...')
                        return render(request, 'admin_template/user_management/edit_user.html')
                    else:
                        user.username = username
                if phone_number and user.phone_number != phone_number :
                    if NewUser.objects.filter(phone_number=phone_number):
                        messages.add_message(request, messages.WARNING, 'Phone Number exist')
                        return render(request, 'admin_template/user_management/edit_user.html')
                    else:
                        user.username = username
                if status and user.status != status :
                    user.status = status
                if password : user.password = password
                user.save()                
    return redirect('admin_app:userinfo')

def deleteuser(request,pk):
    if request.user.is_superuser:
        if NewUser.objects.filter(user_id = pk):
            user = NewUser.objects.get(user_id = pk)
            print(user)
            if not user.is_superuser:
                user.delete()
    return redirect('admin_app:userinfo')
   

def user_control(request):
    pass
    # if not request.user.is_admin:
    #     return redirect('user_app:home')
    # try:
    #     user = NewUser.objects.get(user_id=user_id)
    # except Exception as e:
    #     print(e)

   

