from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponseBadRequest
from django.contrib import messages
from .models import Wallet, Transaction,NewUser
from django.conf import settings
import json
import razorpay
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction
# Create your views here.
#=================  WALLET ====================
def wallet(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})
    transactions = Transaction.objects.filter(wallet=wallet).all().order_by('-id')
    context = {'wallet': wallet, 'transactions': transactions}
    if request.method == 'POST':
        currency = 'INR'
        amount = int(json.loads(request.body)['amount']) 
        user = NewUser.objects.get(email=user.email)

        # Serialize user data and store in cache
        data = {'amount': amount}
        serialized_data = json.dumps(data)
        cache.set('payment_data', serialized_data)

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
        try:
            # Create Razorpay order
            data = {
                'amount':(int(amount)* 100),
                'currency':'INR',
                #'payment_capture':1
            }
            payment1 = client.order.create(data=data)
            payment_order_id = payment1['id']
            context = {
                'amount': amount,
                'payment_order_id': payment_order_id,
                'RAZOR_PAY_KEY_ID': settings.RAZOR_PAY_KEY_ID,
                'payment1':payment1
            }

            return JsonResponse(context)
        except Exception as e:
            print('Error creating Razorpay order:', str(e))
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    # return render(request, 'profile/my-wallet.html', {'user': user})
    return render(request, 'profile/my-wallet.html',context)



# @transaction.atomic
@csrf_exempt
def paymenthandler2(request):
    # user_id = request.GET.get('user_id')
    # user= NewUser.objects.get(user_id=user_id)
    # # return HttpResponseBadRequest()
    # request.user = user
    # only accept POST request.
    if request.method == "POST":
        try:
            # Extract payment details from the POST request
            payment_id        = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature         = request.POST.get('razorpay_signature', '')
            # Create a dictionary of payment parameters
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)
            if not result :
                # Payment signature verification failed
                return render(request, 'profile/paymentfail.html')
                # return JsonResponse({'message': 'Payment signature verification failed'})
            else:
                print(request.user)
                amount = int(request.GET.get('amount'))
                user_id = request.GET.get('user_id')
                if amount:
                    user= NewUser.objects.get(user_id=user_id)
                    wallet=Wallet.objects.get(user=user)
                    wallet.balance+=amount
                    Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT')
                    wallet.save()
                    messages.success(request, f"₹{amount} has been credited to the wallet!")
                    return redirect('user_app:wallet')  
                else:
                    return render(request, 'profile/paymentfail.html')
        except Exception as e:
            # Exception occurred during payment handling
            print('Exception:', str(e))
            # return HttpResponseBadRequest()                         
            return redirect('user_app:payment_failed')  


    else:
        # Redirect to login page if request method is not POST
        return redirect('user_app:view_store')
    
def payment_failed(request):
    return render(request, 'profile/paymentfail.html')

    