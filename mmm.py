
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

#----------------checkout initial code
def checkout(request, total=0, quantity=0, cart_items = None):
    try:
        tax=0
        grand_total = 0
        if request.user.is_authenticated:
            print("cart/checkout/user is authenticated")
            cart_items = CartItem.objects.filter(user=request.user, is_stock=True)
        else:
            print("cart/checkout/user is not authenticated")
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_stock=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.sale_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    addresses = Addresses.objects.filter(user=request.user, is_active=True).order_by('-is_default')
    form = AddressForm(user=request.user)
    context = {
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'form':form,
        'addresses' : addresses, 
    }