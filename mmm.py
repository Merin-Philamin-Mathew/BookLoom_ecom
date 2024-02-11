
def add_to_cart(request):
    
    if request.method=='POST':
        print('xhfdh')

    print("enters the add_to_cart")
    
    cart_product = {}
    print("empty cart_product")
    try:
        product_id = request.GET['id']
        cart_product[str(product_id)] = {
            'title': request.GET['title'],
            'qty': request.GET['qty'],
            'price': request.GET['price']
        }
        print("values")
        if 'cart_data_obj' in request.session:
            print("checking cart_data_obj is in the session or not")
            if str(product_id) in request.session['cart_data_obj']:
                print("cart_data_obj is in the session")
                cart_data = request.session['cart_data_obj']
                cart_data[str(product_id)]['qty'] = int(cart_product[str(product_id)]['qty'])
                cart_data.update(cart_data)
                print("updated the cart")
                request.session['cart_data_obj'] = cart_data
            else:
                print("again adding the same object")
                cart_data = request.session['cart_data_obj']
        else:
            print("cart_data_obj NOT inthe session")
            request.session['cart_data_obj'] = cart_product

        response_data = {"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])}
        return JsonResponse(response_data)

    except ProductVariant.DoesNotExist:
        response_data = {"error": "Product not found"}
        return JsonResponse(response_data, status=404)
    except Exception as e:
        response_data = {"error": str(e)}

        return JsonResponse(response_data, status=500)

# ----------------add_cart javascript code plus objects----------------------
def add_cart(request):
    print("enters the add_to_cart")
    product_id = request.GET['id']
    title=request.GET['title']
    qty=request.GET['qty']
    price = request.GET['price']
    print(product_id,title,qty,price)
    product = Product.objects.get(id=product_id)
    print(product) 
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))#get the cart using the cart_id present
        print(cart,"session id",cart.cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        print(cart,"new session",cart.cart_id)
    cart.save()

    try:
        cart_item = CartItem.objects.get(product = product, cart = cart)
        cart_item.quantity += 1 #cart_item.quantity = cart_item.quantity+1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()
    return JsonResponse(response_data)


