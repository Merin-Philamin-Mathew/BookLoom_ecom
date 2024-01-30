from django.shortcuts import render, get_object_or_404
from django.shortcuts import render,redirect
from store.models import Category,Product, ProductVariant, AdditionalProductImages
from django.urls import reverse
from django.db.models import Q
            
            #for both urls one with slug and other with no slug 
            #shares same view so put category_slug = None 
def viewstore(request,category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = ProductVariant.objects.filter(product__category=categories, is_active=True)

        products_count = products.count()
    else:
        products = ProductVariant.objects.all().filter(is_active=True)
        products_count = products.count()

    context = {
        "products":products,
        "products_count":products_count
        }

    return render(request, 'user_template/store.html', context)



def product_detail(request, category_slug, product_variant_slug):
    try:
        single_product = ProductVariant.objects.get(category__slug=category_slug, slug=product_variant_slug)
        author_name = single_product.author.author_name
        add_images = AdditionalProductImages.objects.filter(product_variant = single_product)
        product_variants = ProductVariant.objects.filter(product=single_product.product,is_active=True)
        rel_products = Product.objects.filter(Q(category__slug=category_slug) | Q(author__author_name=author_name)).exclude(slug=single_product.slug)

    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'rel_products' : rel_products,
      }
   
    return render(request, 'user_template/single_product_page.html', context)
