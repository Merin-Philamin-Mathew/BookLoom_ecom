from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from . models import NewUser
from store.models import Product,Category, Author, Publication
from store.forms import ProductForm, CategoryForm, AuthorForm, PublicationForm


# Create your views here.
def is_superuser(request):
    user = request.user
    if user.is_superuser:
        return True
    return False

@login_required(login_url='admin_app:admin_login')
def admin_logout(request):
    if not is_superuser(request):
        return redirect('user_app:home')
    logout(request)
    return redirect('admin_app:admin_login')

@never_cache
def admin_login(request):
    if is_superuser(request):
        return redirect('admin_app:admin_dashboard')
        
    if request.method == 'POST':
        uname = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=uname, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_app:admin_dashboard') 
        else:
            messages.add_message(request, messages.WARNING, 'Admin user not found or incorrect password')
    return render(request, 'admin_template/admin-login.html')


@never_cache
@login_required(login_url='admin_app:admin_login')
def admin_dashboard(request):
    if not is_superuser(request):
        return redirect('user_app:home')
    if request.user.is_superuser:
        return render(request, 'admin_template\index.html')


#________________________User_management___________________________________________
#_____________________________________________________________________________________
@login_required(login_url='admin_app:admin_login')
def userinfo(request):
    if not is_superuser(request):
        return redirect('user_app:home')
    users = NewUser.objects.filter(is_superuser = False)
    return render(request, 'admin_template/user_management/all_user.html', {'users':users})


@login_required(login_url='admin_app:admin_login')
def adduser(request):
    if not is_superuser(request):
        return redirect('user_app:home')
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


@login_required(login_url='admin_app:admin_login')
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


@login_required(login_url='admin_app:admin_login')
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
@login_required(login_url='admin_app:admin_login')
def listproducts(request):
    if request.user.is_superuser:
        pro_data = Product.objects.all()
        categories = Category.objects.all().order_by('id')

        context = {'pro_data':pro_data,'all_categories':categories}
        return render(request, 'admin_template/product-category/list-products.html',context)
    else:
        return redirect('user_app:home')


@login_required(login_url='admin_app:admin_login')
def controlproducts(request,slug):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    product = Product.objects.get(slug=slug)
    product.is_available = not product.is_available
    product.save()
    
    return redirect('admin_app:list_products')

       
@login_required(login_url='admin_app:admin_login')
def addproducts(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            thumbnail_image = request.FILES.get('thumbnail_image')  
            
            if form.is_valid():
                form.thumbnail_image = thumbnail_image
                form.save()  
                messages.success(request,'product added')
                return redirect('admin_app:list_products') 
            else:
                error = form.errors
                context = {'form':form, 'error':error}
                return render(request, 'admin_template/product-category/add-products.html',context)
            
        form = ProductForm()
        context = {
            'form':form,
        }       
        return render(request, 'admin_template/product-category/add-products.html',context)
    else:
        return redirect('user_app:home')


@login_required(login_url='admin_app:admin_login')
def editproducts(request,slug):
    if request.user.is_superuser:
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
    
    #after submit button
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)  
            # product_name = request.POST['product_name']
            # description = request.POST['description']
            # slug = request.POST['slug']
            if form.is_valid():
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
                messages.success(request,"Product updated")
                return redirect('admin_app:list_products')
            else:
                error = form.errors
                context = {'form':form, 'error':error}
                return render(request, 'admin_template/product-category/edit-products.html',context)
   
        context = {
            'form': form,
            #'product_variants':product_variants, 
            'slug': slug,
        }
        return render(request,'admin_template/product-category/edit-products.html',context)   
    else:
        return redirect('user_app:home')     


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
@login_required(login_url='admin_app:admin_login')
def listcategory(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    categories = Category.objects.all().order_by('id')

    return render(request, 'admin_template/product-category/category-list.html',{'all_categories':categories})


@login_required(login_url='admin_app:admin_login')
def controlcategory(request, slug):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist as e:
        print(e)

    category.is_active = not category.is_active
    category.save()

    if category.parent_cat is None:
        subcategories = category.subcategories.all()
        for subcategory in subcategories:
            subcategory.is_active = category.is_active
            subcategory.save()

    return redirect('admin_app:category')


@login_required(login_url='admin_app:admin_login')
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

@login_required(login_url='admin_app:admin_login')
def addcategory(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    # import pdb
    # pdb.set_trace()
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Category created")
            return redirect('admin_app:category')
        else:
            print(form.errors)
      
    
    form = CategoryForm()
    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/add-category.html', context)




#________________________Author_management___________________________________________
#_____________________________________________________________________________________
@login_required(login_url='admin_app:admin_login')
def listauthor(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    
    authors = Author.objects.all().order_by('id')
    return render(request, 'admin_template/product-category/list-author.html',{'all_authors':authors}) 

@login_required(login_url='admin_app:admin_login')
def controlauthor(request, slug):
    if request.user.is_superuser:
        try:
            author = Author.objects.get(slug=slug)
        except Author.DoesNotExist as e:
            print(e)

        author.is_active = not author.is_active
        author.save()
        return redirect('admin_app:list_author')
    else:
        return redirect('user_app:home')

@login_required(login_url='admin_app:admin_login')
def editauthor(request,slug): 
    if request.user.is_superuser:

        author = Author.objects.get(slug=slug)
        form = AuthorForm(instance = author)

        if request.method == 'POST':
            form = AuthorForm(request.POST, request.FILES, instance=author)  
      
            if form.is_valid():
                form.save()
                messages.success(request,"Author updated")
                return redirect('admin_app:list_author')
            else:
                error = form.errors
                context = {'form':form, 'error':error}
                return render(request, 'admin_template/product-category/edit-author.html',context)
 
        context = {
            'form': form,
            'slug':slug
        }
        return render(request,'admin_template/product-category/edit-author.html',context)     
    else:
        return redirect('user_app:home')   

@login_required(login_url='admin_app:admin_login')
def addauthor(request): 
    if not request.user.is_superuser:
        return redirect('user_app:home') 
    if request.method == 'POST':
        form = AuthorForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Author created")
            return redirect('admin_app:list_author')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'admin_template/product-category/add-author.html',context)
    
    form = AuthorForm()
    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/add-author.html',context) 

#________________________Publication_management_______________________________________
#_____________________________________________________________________________________
@login_required(login_url='admin_app:admin_login')
def listpublication(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    publications = Publication.objects.all().order_by('id')

    context = {
        'all_publications':publications
    }
    return render(request, 'admin_template/product-category/list-publication.html',context) 

@login_required(login_url='admin_app:admin_login')
def controlpublication(request, id):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        publication = Publication.objects.get(id=id)
    except Publication.DoesNotExist as e:
        print(e)

    publication.is_active = not publication.is_active
    publication.save()
    return redirect('admin_app:list_publication')

@login_required(login_url='admin_app:admin_login')
def editpublication(request,id):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        publication = Publication.objects.get(id=id)
    except Exception as e:
        print(e)
    form = PublicationForm(instance = publication)
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=publication)

        if form.is_valid():
            form.save()
            messages.success(request, "Publication updated")
            return redirect('admin_app:list_publication')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'admin_template/product-category/edit-publication.html',context)

    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/edit-publication.html', context)

@login_required(login_url='admin_app:admin_login')
def addpublication(request):  
    if not request.user.is_superuser:
        return redirect('user_app:home')
    if request.method == 'POST':
        form = PublicationForm(request.POST,request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Publication created")
            return redirect('admin_app:list_publication')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'admin_template/product-category/add-publication.html',context)
            
    form = PublicationForm()
    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/add-publication.html',context) 

