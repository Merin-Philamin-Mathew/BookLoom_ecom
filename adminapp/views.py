from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from . models import NewUser
from store.models import Product,Category
from store.forms import ProductForm, CategoryForm

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

#________________________User_management___________________________________________
#_____________________________________________________________________________________

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

""" def deleteuser(request,slug):
    if request.user.is_superuser:
        if NewUser.objects.filter(user_id = slug):
            user = NewUser.objects.get(user_id = slug)
            if not user.is_superuser:
                user.delete()
    return redirect('admin_app:userinfo') """
   

def controluser(request,user_id):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        user = NewUser.objects.get(user_id=user_id)
    except Exception as e:
        print(e)

    user.status = (
    'blocked' if user.status == 'active' else
    'unblocked' if user.status == 'blocked' else
    'blocked'
)

    user.save()
    
    return redirect('admin_app:userinfo')


#________________________Product_management___________________________________________
#_____________________________________________________________________________________
def listproducts(request):
    if request.user.is_superuser:
        pro_data = Product.objects.all()
        categories = Category.objects.all().order_by('id')

        context = {'pro_data':pro_data,'all_categories':categories}
        return render(request, 'admin_template/product-category/list-products.html',context)

def controlproducts(request,slug):
    product = Product.objects.get(slug=slug)
    product.is_available = not product.is_available
    product.save()
    
    return redirect('admin_app:list_products')


def addproducts(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                form.save()  
                messages.success(request,'product added')
            return redirect('admin_app:list_products') 
        form = ProductForm()
        context = {
            'form':form
        }       
    return render(request, 'admin_template/product-category/add-products.html',context)

def editproducts(request,slug):
    if request.user.is_superuser:
        print('user is supser user ----------------------------------------------------------')
        product = Product.objects.get(slug=slug)
        #if varients take that also
        #product_variants = ProductVariant.objects.filter(product = product)
        form = ProductForm(instance = product)

        # if request.method == 'GET':
        #     proinfo = Product.objects.get(slug=slug)
        #     context = {
        #         'pro_data':proinfo
        #     }
        #     return render(request, 'admin_template/product-category/edit-products.html',context)
        print("values passed------------------------------------------------------------------------------------------")
    #after submit button
    if request.method == 'POST':
        print("method is post----------------------------------------------------------------------------")
        form = ProductForm(request.POST,instance=product)  
        print("form.......................................................................................",form)
        # product_name = request.POST['product_name']
        # description = request.POST['description']
        # slug = request.POST['slug']

        if form.is_valid():
            print("form is valid-------------------------------------------------------------------------------")
        # proinfo = Product.objects.get(slug=slug)
        # if product_name and proinfo.product_name != product_name:
        #     if Product.objects.filter(product_name=product_name):
        #         messages.add_message(request, messages.WARNING, 'product exists' )
        #         return render(request,'admin_template/product-category/edit-products.html')
        #     else:
        #         proinfo.product_name = product_name

        # if proinfo.description != description:
        #     proinfo.description = description
            
        # if proinfo.slug != slug:
        #     if Product.objects.filter(slug=slug):
        #         messages.add_message(request, messages.WARNING, 'slug exists' )
        #         return render(request,'admin_template/product-category/edit-products.html')
        #     else:
        #         proinfo.slug = slug
            form.save()
            print("form is saved.........................................................................")
            messages.success(request,"Product updated")
            return redirect('admin_app:list_products')
        
    context = {
        'form': form,
        #'product_variants':product_variants, 
        'slug': slug,
    }
    return render(request,'admin_template/product-category/edit-products.html',context)        


#________________________Category_management___________________________________________
#_____________________________________________________________________________________
""" def listcategory(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            #save new categories if method='POST'
            cat_name = request.POST['category_name']
            slug = request.POST['slug']
            description = request.POST['description']
            parent = request.POST['parent']
            catinfo = Category(category_name=cat_name, slug=slug, description=description,parent=parent)
            catinfo.save()
        #listing the category objects
        cat_data = Category.objects.all()
        context = {'cat_data':cat_data}
        return render(request, 'admin_template/product-category/category-list.html', context)
    return render(request, 'admin_template/product-category/category-list.html')
 """
def listcategory(request):
    
    categories = Category.objects.all().order_by('id')

    context = {
        'all_categories':categories
    }
    return render(request, 'admin_template/product-category/category-list.html',context)

def controlcategory(request, slug):
    try:
        category = Category.objects.get(slug = slug)
    except Exception as e:
        print(e)
    
    category.is_active = not category.is_active
    category.save()
    return redirect('admin_app:category')

def editcategory(request,slug):
    try:
        category = Category.objects.get(slug=slug)
    except Exception as e:
        print(e)
    form = CategoryForm(instance = category)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated")
            return redirect('admin_app:category')

    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/edit-category.html', context)

    if request.user.is_superuser:
        if request.method == "GET":
            #checking if there is a slug in the database of the model of Category like the request
            if Category.objects.filter(slug = slug):
                #if yes then retriev that object details
                catinfo = Category.objects.get(id = slug)
                #and pass it in a variable
                context = {
                    'cat_data':catinfo
                }
                #pass the details to the front end
                return render(request, 'admin_template/product-category/edit-category.html', context)
        elif request.method == 'POST':
            cat_name = request.POST['category_name']
            slug = request.POST['slug']
            description = request.POST['description']
            parent = request.POST['parent']
            
            if Category.objects.filter(id=slug):
                #checking the userdata before and after editing are not the same
                #befor saving the post form 
                #if any data of anyfield is same==changes are not done.
                #no need to go to that field again
                catinfo = Category.objects.get(id=slug)
                if cat_name and catinfo.category_name != cat_name:
                    if Category.objects.filter(category_name=cat_name):
                        messages.add_message(request, messages.WARNING, 'category_name exist')
                        return render(request, 'admin_template/product-category/edit-category.html')
                    else:
                        catinfo.category_name = cat_name
                if description and catinfo.description != description :
                    if Category.objects.filter(description=description):
                        messages.add_message(request, messages.WARNING, 'description exist...')
                        return render(request, 'admin_template/product-category/edit-category.html')
                    else:
                        catinfo.description = description
                if slug and catinfo.slug != slug:
                    if Category.objects.filter(slug=slug):
                        messages.add_message(request, messages.WARNING, 'Slug exist')
                        return render(request, 'admin_template/product-category/edit-category.html')
                    else:
                        catinfo.slug = slug
                if parent and catinfo.parent != parent :
                    catinfo.parent = parent
                catinfo.save()                
    return redirect('store_app:category')

def addcategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Category created")
            return redirect('admin_app:list_category')
    
    form = CategoryForm()
    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/add-category.html', context)



