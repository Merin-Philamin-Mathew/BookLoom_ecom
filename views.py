from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout

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
        phone = request.POST['phone_number']

        user = authenticate(username=uname, password=password, phone_number=phone)
        if user is not None:
            login(request, user)
            return redirect('admin_app:admin_dashboard') 
        # else:
        #     if User.objects.filter(username=uname):
        #         messages.add_message(request, messages.WARNING, 'Invalid password')
        #     else:
        #         messages.add_message(request, messages.WARNING, 'Not admin')
    return render(request, 'admin_template/admin-login.html')


def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, 'admin_template\index.html')

