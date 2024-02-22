from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from . models import NewUser, Coupon
from . forms import CouponForm 
from store.models import Product,Category, Author, Publication, ProductVariant, AdditionalProductImages, Language
from store.forms import ProductForm, ProductVariantForm, AddProImgForm, CategoryForm, AuthorForm, PublicationForm, LanguageForm
from orders.models import Order, Payment, OrderProduct

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
        pro_data = ProductVariant.objects.all().order_by('product')
      
        categories = Category.objects.all().order_by('id')

        context = {'pro_data':pro_data,'all_categories':categories}
        return render(request, 'admin_template/product-category/list-products.html',context)
    else:
        return redirect('user_app:home')


@login_required(login_url='admin_app:admin_login')
def controlproducts(request,slug):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    product = ProductVariant.objects.get(product_variant_slug=slug)
    product.is_active = not product.is_active
    product.save()

    return redirect('admin_app:list_products')    

       
@login_required(login_url='admin_app:admin_login')
def addproducts(request):
    
    if request.user.is_superuser:
  
        thumbnail_image = request.FILES.get('thumbnail_image')  
        
        if request.method == 'POST':
            author_form = AuthorForm(request.POST, request.FILES)
            proform = ProductForm(request.POST)
            form = ProductVariantForm(request.POST, request.FILES)
            add_img_form = AdditionalProductImages(request.POST, request.FILES)
            print("pro",proform.errors)
            print("var",form.errors)   
            print("author",author_form.errors)   
            # if author_form.is_valid():
            #     author = author_form.save()
            
            
            if all([form.is_valid(), proform.is_valid()]):
                
                product = proform.save(commit=False)
                product.save()
                product_variant = form.save(commit=False)
                product_variant.product = product
                provar = product_variant.save()
                # addimg = add_img_form.save = ()
                # adobj = AdditionalProductImages.objects.all()
                # adobj.product_variant = provar
                # adobj.image = addimg
                # adobj.is_active = True
                # adobj.save()
                

                messages.success(request,'product added successfully')
                return redirect('admin_app:list_products') 
            else:
                error = form.errors
                proerror = proform.errors
                context = {'form':form, 'error':error, 'proform':proform,'proerror':proerror}
                print("error",error)
                print("proerror",proerror)
                return render(request, 'admin_template/product-category/add-products.html',context)
        else:
            authorform = AuthorForm()
            proform = ProductForm()
            form =  ProductVariantForm()
            add_img_form = AddProImgForm()
        
        
            context = {
                'proform':proform,
                'form':form,
                'authorform':authorform,
                'addimgfrom':add_img_form
            }       
            return render(request, 'admin_template/product-category/add-products.html',context)
    else:
        return redirect('user_app:home')


@login_required(login_url='admin_app:admin_login')
def editproducts(request,slug):
    if request.user.is_superuser:
        productvar = ProductVariant.objects.get(product_variant_slug=slug)   
        product = Product.objects.get(product_name=productvar.product)
     
        form = ProductVariantForm(instance = productvar)
        proform = ProductForm(instance = product)
        additional_images = AdditionalProductImages.objects.filter(product_variant=productvar)
      
        if request.method == 'POST':
            
            form = ProductVariantForm(request.POST, request.FILES, instance=productvar)  
            #additional_image_form = AddProImgForm(request.POST, request.FILES)
            images = request.FILES.getlist('image')
            
            proform = ProductForm(request.POST,instance=product)
            
            if all([form.is_valid(), proform.is_valid()]):
                product = proform.save(commit=False)
                product.save()
                product_variant = form.save(commit=False)
                product_variant.product = product
                product_variant.save()

                for image in images:
                    AdditionalProductImages.objects.create(product_variant=product_variant, image=image)
                product_variant.save()

                messages.success(request,"Product updated")
                return redirect('admin_app:list_products')
            else:
                error = form.errors
                proerror = proform.errors
                context = {'form':form,'proform':proform, 'error':error, 'proerror':proerror}
                return render(request, 'admin_template/product-category/edit-products.html',context)
   
        context = {
            'form': form,
            'proform':proform,
            #'additional_images': additional_images,
            'slug': slug,
        }
        return render(request,'admin_template/product-category/edit-products.html',context)   
    else:
        return redirect('user_app:home')     

#product variants
@login_required(login_url='admin_app:admin_login')
def addproductvariant(request,slug):
    if request.user.is_superuser:
        productvar = ProductVariant.objects.get(product_variant_slug=slug)   
        product = Product.objects.get(product_name=productvar.product)
     
        form = ProductVariantForm()
        proform = ProductForm(instance = product)
        proform.is_translated = True

        if request.method == 'POST':
            form = ProductVariantForm(request.POST, request.FILES)  
            proform = ProductForm(request.POST)
            if form.is_valid():
                product_variant = form.save(commit=False)
                product_variant.product = product
                product_variant.save()

                product.is_translated = True
                product.save()
                messages.success(request,"Product variant added")
                return redirect('admin_app:list_products')
            else:
                error = form.errors
                proerror = proform.errors
                print("var",error)
                print("pro",proerror)
                context = {'form':form,'proform':proform, 'error':error, 'proerror':proerror}
                return render(request, 'admin_template/product-category/add-pro-variant.html',context)
   
        context = {
            'form': form,
            'proform':proform,
            'slug': slug,
        }
        return render(request,'admin_template/product-category/add-pro-variant.html',context)   
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


#________________________language_management_______________________________________
#_____________________________________________________________________________________

@login_required(login_url='admin_app:admin_login')
def listlanguage(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    languages = Language.objects.all().order_by('id')

    context = {
        'all_languages':languages
    }
    return render(request, 'admin_template/product-category/list-language.html',context) 

@login_required(login_url='admin_app:admin_login')
def controllanguage(request, id):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        language = Language.objects.get(id=id)
    except Language.DoesNotExist as e:
        print(e)

    language.is_active = not language.is_active
    language.save()
    return redirect('admin_app:list_language')

@login_required(login_url='admin_app:admin_login')
def editlanguage(request,id):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    try:
        language = Language.objects.get(id=id)
    except Exception as e:
        print(e)
    form = LanguageForm(instance = language)
    
    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=language)

        if form.is_valid():
            form.save()
            messages.success(request, "language updated")
            return redirect('admin_app:list_language')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'admin_template/product-category/edit-language.html',context)

    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/edit-language.html', context)


@login_required(login_url='admin_app:admin_login')
def addlanguage(request):  
    if not request.user.is_superuser:
        return redirect('user_app:home')
    if request.method == 'POST':
        form = LanguageForm(request.POST,request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request, "language created")
            return redirect('admin_app:list_language')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'admin_template/product-category/add-language.html',context)
            
    form = LanguageForm()
    context = {
        'form':form
    }
    return render(request, 'admin_template/product-category/add-language.html',context) 



# def editproducts(request,slug):
#     if request.user.is_superuser:
#         productvar = ProductVariant.objects.get(product_variant_slug=slug)   
#         pro = productvar.product.all()
#         print(pro,'pro')
#         #if varients take that also
#         #product_variants = ProductVariant.objects.filter(product = product)
#         form = ProductVariantForm(instance = productvar)
#         proform = ProductForm(instance = product)
#         # if request.method == 'GET':
#         #     proinfo = Product.objects.get(slug=slug)
#         #     context = {
#         #         'pro_data':proinfo
#         #     }
#         #     return render(request, 'admin_template/product-category/edit-products.html',context)
    
#     #after submit button
#         if request.method == 'POST':
#             form = ProductVariantForm(request.POST, request.FILES, instance=productvar)  
#             proform = ProductForm(request.POST,instance=product)
#             # product_name = request.POST['product_name']
#             # description = request.POST['description']
#             # slug = request.POST['slug'] 
#             if all([form.is_valid(), proform.is_valid()]):
#            # proinfo = Product.objects.get(slug=slug)
#             # if product_name and proinfo.product_name != product_name:
#             #     if Product.objects.filter(product_name=product_name):
#             #         messages.add_message(request, messages.WARNING, 'product exists' )
#             #         return render(request,'admin_template/product-category/edit-products.html')
#             #     else:
#             #         proinfo.product_name = product_name

#             # if proinfo.description != description:
#             #     proinfo.description = description
                
#             # if proinfo.slug != slug:
#             #     if Product.objects.filter(slug=slug):
#             #         messages.add_message(request, messages.WARNING, 'slug exists' )
#             #         return render(request,'admin_template/product-category/edit-products.html')
#             #     else:
#             #         proinfo.slug = slug
#                 product = proform.save(commit=False)
#                 product.save()
#                 product_variant = form.save(commit=False)
#                 product_variant.product = product
#                 product_variant.save()
#                 messages.success(request,"Product updated")
#                 return redirect('admin_app:list_products')
#             else:
#                 error = form.errors
#                 context = {'form':form, 'error':error}
#                 return render(request, 'admin_template/product-category/edit-products.html',context)
   
#         context = {
#             'form': form,
#             #'product_variants':product_variants, 
#             'slug': slug,
#         }
#         return render(request,'admin_template/product-category/edit-products.html',context)   
#     else:
#         return redirect('user_app:home') 

#________________________order_management_______________________________________
#_____________________________________________________________________________________
@login_required(login_url='admin_app:admin_login')
def listorder(request):
    if not request.user.is_superuser:
        return redirect('user_app:home')
    orders = Order.objects.all().order_by('-id')

    context = {
        'all_orders':orders
    }
    return render(request, 'admin_template/order_management/list-orders.html',context) 

@login_required(login_url='admin_app:admin_login')
def change_order_status(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    order_ = Order.objects.get(order_number=id)
    status = request.POST.get('status')
    user = order_.user
    if status == "Delivered":
        order_.deliverd_at = timezone.now()
        total = order_.order_total
    elif status == "Returned":
        order_.returned_at = timezone.now()
        total = order_.order_total
       
    else:
        order_.deliverd_at = None

    if status:
        order_.order_status = status
    order_.save()

    # Add success message for successful status change
    messages.success(request, 'Order status updated successfully.')

    return redirect('admin_app:list_order')


#________________________language_management_______________________________________
#_____________________________________________________________________________________

@login_required(login_url='admin_app:admin_login')
def coupons(request):
    print("admin_app/coupon")
    if not is_superuser(request):
        return redirect('user_app:home')
    coupon = Coupon.objects.all().order_by('-created_at')
    context = {
        'coupon': coupon,
    }
    
    return render(request, 'admin_template/coupon_management/coupon.html',context)

@login_required(login_url='admin_app:admin_login')
def add_coupons(request):
    if not is_superuser(request):
        return redirect('user_app:home')
    if request.method == "POST":
        form = CouponForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon added successfully.')
            return redirect('admin_app:coupons')
        else:
            messages.error(request, 'Error: Invalid data. Please check the form.')
    else:
        form = CouponForm()
    coupon = Coupon.objects.all().order_by('-created_at')
    context = {
        "form": form,
        'coupon': coupon,
    }
    return render(request, 'admin_template/coupon_management/coupon.html', context)

@login_required(login_url='admin_app:admin_login')
def activate_coupon(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        pi = Coupon.objects.get(id=id)
        pi.active = True
        pi.save()
        messages.success(request, 'Coupon activated successfully.')
    return redirect('admin_app:coupons')

@login_required(login_url='accounts:signin')
def disable_coupon(request, id):
    if not is_superuser(request):
        return redirect('store:home')
    if request.method == 'POST':
        pi = Coupon.objects.get(id=id)
        pi.active = False
        pi.save()
        messages.success(request, 'Coupon disabled successfully.')
    return redirect('admin_app:coupons')


