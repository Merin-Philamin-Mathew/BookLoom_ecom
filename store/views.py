from django.shortcuts import render,redirect
from . models import Category,Product
from django.contrib import messages

#____________________________category management______________________________________
#_____________________________________________________________________________________
def listcategory(request):
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

def editcategory(request,pk):
    if request.user.is_superuser:
        if request.method == "GET":
            #checking if there is a pk in the database of the model of Category like the request
            if Category.objects.filter(id = pk):
                #if yes then retriev that object details
                catinfo = Category.objects.get(id = pk)
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
            
            if Category.objects.filter(id=pk):
                #checking the userdata before and after editing are not the same
                #befor saving the post form 
                #if any data of anyfield is same==changes are not done.
                #no need to go to that field again
                catinfo = Category.objects.get(id=pk)
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

def deletecategory(request,pk):
    if request.user.is_superuser:
        if Category.objects.filter(id=pk):
            catinfo = Category.objects.get(id=pk)
            catinfo.delete()
            return redirect('store_app:category')
            """ if catinfo.is_child:
                catinfo.delete()
                return render(request, 'admin_template/product-category/category-list.html') """


#________________________Product_management___________________________________________
#_____________________________________________________________________________________
def listproducts(request):
    if request.user.is_superuser:
        pro_data = Product.objects.all()
        context = {'pro_data':pro_data}
        return render(request, 'admin_template/product-category/list-products.html',context)

def addproducts(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product_name = request.POST['product_name']
            description = request.POST['description']
            max_price = request.POST['max_price']
            sale_price = request.POST['sale_price']
            #thumbnail_image = request.FILES['thumbnail_image']
            slug = request.POST['slug']
            

            proinfo = Product(product_name=product_name, long_description=description,max_price=max_price, sale_price=sale_price, slug=slug)
            proinfo.save()  
            return redirect('store_app:list_products')        
    return render(request, 'admin_template/product-category/add-products.html')

def editproducts(request,pk):
    if request.user.is_superuser:
        if request.method == 'GET':
            proinfo = Product.objects.get(id=pk)
            context = {
                'pro_data':proinfo
            }
            return render(request, 'admin_template/product-category/edit-products.html',context)

        elif request.method == 'POST':
            product_name = request.POST['product_name']
            description = request.POST['description']
            slug = request.POST['slug']

            proinfo = Product.objects.get(id=pk)
            if product_name and proinfo.product_name != product_name:
                if Product.objects.filter(product_name=product_name):
                    messages.add_message(request, messages.WARNING, 'product exists' )
                    return render(request,'admin_template/product-category/edit-products.html')
                else:
                    proinfo.product_name = product_name

            if proinfo.description != description:
                proinfo.description = description
            
            if proinfo.slug != slug:
                if Product.objects.filter(slug=slug):
                    messages.add_message(request, messages.WARNING, 'slug exists' )
                    return render(request,'admin_template/product-category/edit-products.html')
                else:
                    proinfo.slug = slug
            proinfo.save()
            return redirect('store_app:list_products')
              


def deleteproducts(request,pk):
    if request.user.is_superuser:
        if Product.objects.filter(id=pk):
            proinfo = Product.objects.get(id=pk)
            proinfo.delete()
            return redirect('store_app:list_products')   
