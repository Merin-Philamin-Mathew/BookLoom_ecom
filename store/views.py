from django.shortcuts import render, get_object_or_404
from django.shortcuts import render,redirect
from store.models import Category,Product, ProductVariant, AdditionalProductImages
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse,HttpResponse
            
            #for both urls one with slug and other with no slug 
            #shares same view so put category_slug = None 
def viewstore(request,category_slug=None):
    categories = None
    products = None
    search_word = ''  # Initialize search_word

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = ProductVariant.objects.filter(product__category=categories, is_active=True)
    else:
        products = ProductVariant.objects.all().filter(is_active=True)
        
    if request.method == 'POST':
        search_word = request.POST['search-word']
        products = ProductVariant.objects.filter(
            Q(product__product_name__icontains = search_word)|
            Q(long_description__icontains = search_word)|
            Q(product__author__author_name__icontains = search_word)
        ).order_by('id')

    products_count = products.count()

    context = {
        "products":products,
        "products_count":products_count,
        'search_word':search_word,
        }

    return render(request, 'user_template/store.html', context)

def product_detail(request, category_slug, product_variant_slug):
    try:
        print("bleeeeeedfsdfeeeeeeeeeeesh")
        print("cat slug:",category_slug,"provar slug:", product_variant_slug)
        single_product = ProductVariant.objects.get(product__category__slug=category_slug, product_variant_slug=product_variant_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
        author_name = single_product.product.author.author_name
        print("kmkj",category_slug)
        # add_images = AdditionalProductImages.objects.filter(product_variant = single_product)
        # product_variants = ProductVariant.objects.filter(product=single_product.product,is_active=True)
        rel_products = ProductVariant.objects.filter(Q(product__category__slug=category_slug) | Q(product__author__author_name=author_name)).exclude(product_variant_slug =single_product.product_variant_slug)
    except ProductVariant.DoesNotExist as e:
        print(e)
        return render(request, '404.html')

    
    context = {
        'single_product': single_product,
        'rel_products' : rel_products,
        'in_cart' : in_cart,
      }
   
    return render(request, 'user_template/single_product_page.html', context)



def add_to_cart(request):
    print("enters the add_to_cart")
    
    cart_product = {}
    print("empty cart_product")
    try:
        print('try')
        product_id = request.GET['id']
        cart_product[str(product_id)] = {
            'title': request.GET['title'],
            'qty': request.GET['qty'],
            'price': request.GET['price']
        }
        print("checking cart_data_obj is in the session or not")
        
        if 'cart_data_obj' in request.session:
            print("cart_data_obj is in the session")
            if str(product_id) in request.session['cart_data_obj']:
                cart_data = request.session['cart_data_obj']
                cart_data[str(product_id)]['qty'] = int(cart_product[str(product_id)]['qty'])
                cart_data.update(cart_data)
                print("updated the cart")
                request.session['cart_data_obj'] = cart_data
            else:
                print("creating the cart of the product1 for the first time")
                cart_data = request.session['cart_data_obj']
                cart_data.update(cart_product)
                request.session['cart_data_obj'] = cart_data
        else:
            print("cart_data_obj NOT inthe session")
            request.session['cart_data_obj'] = cart_product

        response_data = {"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])}
        print(response_data)
        return JsonResponse(response_data)

    except ProductVariant.DoesNotExist:
        response_data = {"error": "Product not found"}
        return JsonResponse(response_data, status=404)
    except Exception as e:
        response_data = {"error": str(e)}
        return JsonResponse(response_data, status=500)

