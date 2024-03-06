from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum
from . models import NewUser, Coupon
from . forms import CouponForm 
from store.models import Product,Category, Author, Publication, ProductVariant, AdditionalProductImages, Language
from store.forms import ProductForm, ProductVariantForm, CategoryForm, AuthorForm, PublicationForm, LanguageForm
from orders.models import Order, Payment, OrderProduct

from datetime import date,timedelta
from django.views import View
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.conf import settings
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


def get_month_name(month):
    months_in_english = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return months_in_english[month]
@never_cache
@login_required(login_url='admin_app:admin_login')
def admin_dashboard(request):
    if not is_superuser(request):
        return redirect('user_app:home')
    products = ProductVariant.objects.all()
    orders = Order.objects.filter(is_ordered = True)
    categories = Category.objects.all()
    payments = Payment.objects.filter(payment_status = 'SUCCESS')
    revenue = 0
    for payment in payments.all():
        revenue += payment.amount_paid
        # Calculate monthly revenue
    current_month = timezone.now().month
    monthly_payments = Payment.objects.filter(
        payment_status='SUCCESS',
        created_at__month=current_month
    )
    monthly_revenue = monthly_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=180)
    data = [['Month', 'New User Signups', 'New Orders']]
    while start_date < current_datetime:
        end_date = start_date.replace(day=1) + timedelta(days=31)
        new_user_signups = NewUser.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date).count()
        new_orders = Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        month_name = get_month_name(start_date.month)
        data.append([month_name, new_user_signups, new_orders])
        start_date = end_date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    print("dfds",start_date,end_date,)
    # Filter orders based on date range and status
    all_orders = Order.objects.all().order_by('-id')
    if start_date and end_date:
        all_orders = all_orders.filter(created_at__gte=start_date, created_at__lt=end_date)
    elif start_date:
        all_orders = all_orders.filter(created_at__gte=start_date)
    elif end_date:
        all_orders = all_orders.filter(created_at__lt=end_date)
    if status and status != 'Status':
        print("0000000000000000000000000000",status)
        all_orders = all_orders.filter(order_status=status)

    
    context = {
        "revenue":revenue,
        "monthly_revenue":monthly_revenue,
        "orders":orders,
        "all_orders":all_orders,
        "order_count":orders.count(),
        "product_count":products.count(),
        "category_count":categories.count(),
        'data': data,

    }
    return render(request, 'admin_template\index.html', context)


class SalesReportPDFView(View):
    def save_pdf(self,params:dict):
        template = get_template("admin_template/sales_report.html")
        html = template.render(params)
        response = BytesIO()
        pdf =pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
        
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf'),True
        return '',None
    # @login_required(login_url='accounts:signin')
    def get(self, request, *args, **kwargs):
        # if not is_superuser(request):
        #     return redirect('store:home')
        total_users = len(NewUser.objects.all())
        new_orders = len(Order.objects.all().exclude(order_status="new"))
        revenue_total = 0
        payments = Payment.objects.filter(payment_status = 'SUCCESS')
        revenue_total = 0
        for payment in payments.all():
            revenue_total += payment.amount_paid    
        current_date = date.today()

        current_month = timezone.now().month
        monthly_payments = Payment.objects.filter(
        payment_status='SUCCESS',
        created_at__month=current_month
        )
        monthly_revenue = monthly_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status = request.GET.get('status')
        print("dfds",start_date,end_date,)
        # Convert start_date and end_date to timezone-aware datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d')) if start_date else None
        end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d')) if end_date else None

        # Filter orders based on date range and status
        all_orders = Order.objects.all()
        if start_date and end_date:
            all_orders = all_orders.filter(created_at__gte=start_date, created_at__lt=end_date)
        elif start_date:
            all_orders = all_orders.filter(created_at__gte=start_date)
        elif end_date:
            all_orders = all_orders.filter(created_at__lt=end_date)
        if status and status != 'Status':
            all_orders = all_orders.filter(order_status=status)
      
        # delivered_orders_this_month = Order.objects.filter(
        #     payment=payments,
        #     deliverd_at__year=current_date.year,
        #     deliverd_at__month=current_date.month
        # )
        # month_len = len(delivered_orders_this_month)
        # revenue_this_month = delivered_orders_this_month.aggregate(Sum('order_total'))['order_total__sum']
        # # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        # return response
        print("dfsddfsfsdsdfsdf",all_orders)
        params = {
            'total_users' :total_users,
            'new_orders' : new_orders,
            'revenue_total' : revenue_total,
            # 'd_month' :delivered_orders_this_month,
            'd_month_len' : len(monthly_payments),
            'revenue_this_month' : monthly_revenue,
            'all_orders': all_orders,  # Pass filtered orders to the template

        }
        file_name, success = self.save_pdf(params)
        
        if success:
            response = HttpResponse(file_name, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
            return response
        else:
            # Handle error case here, like displaying an error message to the user.
            return HttpResponse("Failed to generate the invoice.", status=500)



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
            # author_form = AuthorForm(request.POST, request.FILES)
            proform = ProductForm(request.POST)
            images = request.FILES.getlist('image')
            form = ProductVariantForm(request.POST, request.FILES)
            # add_img_form = AdditionalProductImages(request.POST, request.FILES)
            print("proform.errors",proform.errors)
            print("form.errors",form.errors)   
            # print("author",author_form.errors)   
            # if author_form.is_valid():
            #     author = author_form.save()
            
            
            if all([form.is_valid(), proform.is_valid()]):
                
                product = proform.save(commit=False)
                product.save()
                product_variant = form.save(commit=False)
                product_variant.product = product
                product_variant.save()
                # addimg = add_img_form.save = ()
                # adobj = AdditionalProductImages.objects.all()
                # adobj.product_variant = provar
                # adobj.image = addimg
                # adobj.is_active = True
                # adobj.save()
                for image in images:
                    AdditionalProductImages.objects.create(product_variant=product_variant, image=image)
                product_variant.save()

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
            # authorform = AuthorForm()
            proform = ProductForm()
            form =  ProductVariantForm()
    
        
            context = {
                'proform':proform,
                'form':form,
                # 'authorform':authorform,
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
        # additional_images = AdditionalProductImages.objects.filter(product_variant=productvar)
      
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
            images = request.FILES.getlist('image')

            if form.is_valid():
                product_variant = form.save(commit=False)
                product_variant.product = product
                product_variant.save()
                product.is_translated = True
                product.save()
                for image in images:
                    AdditionalProductImages.objects.create(product_variant=product_variant, image=image)
                product_variant.save()
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
        if order_.payment.payment_method == 'Cash on Delivery':
            order_.payment.payment_status = 'SUCCESS'

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


