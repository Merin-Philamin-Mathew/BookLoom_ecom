from django.db import models
# Create your models here.
from datetime import timedelta, timezone
from django.db import models
from cart.models import Cart,CartItem
from adminapp.models import Addresses,Profile,NewUser
from store.models import Product,ProductVariant

# Create your models here.
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES =(
    ("PENDING", "Pending"),
    ("FAILED", "Failed"),
    ("SUCCESS", "Success"),
    )
    payment_id  = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=50)
    payment_status      = models.CharField(default='PENDING', choices = PAYMENT_STATUS_CHOICES,max_length=20)
    created_at  = models.DateTimeField(auto_now_add=True)
    #is_paid             = models.BooleanField(default=False)
    
    def __str__(self):
        return self.payment_order_id

    """ spike_use = models.BooleanField(default=False)
    spike_discount = models.PositiveBigIntegerField(default = 0)
    coupon_use = models.BooleanField(default = False)
    coupon_discount = models.PositiveIntegerField(default=0)
    coupon_code = models.CharField(max_length=50,default='') """
     
    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Confirmed','Confirmed'),
        ('shipping','shipping'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Return initiated','Return initiated'),
        ('Returned','Returned'),
    )
    
    
    user    = models.ForeignKey(NewUser, on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null= True) 
    order_number = models.CharField(max_length=50)
    address = models.ForeignKey(Addresses,on_delete=models.SET_NULL,unique=False, null= True ,blank=True,)
    order_note = models.CharField(max_length=50, blank=True)
    order_total = models.FloatField( )
    tax = models.FloatField( )
    order_status = models.CharField(max_length=50,choices=STATUS,default='New')
    ip = models.CharField(max_length=50,blank=True)
    is_ordered = models.BooleanField(default= False)
    razor_pay_order_id = models.CharField(max_length= 100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length= 100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length= 100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deliverd_at = models.DateTimeField(null=True)
    returned_at = models.DateTimeField(null=True)
    

    def __str__(self):
        return self.order_number

    
    def can_return_products(self):
        if self.delivered_at:
            current_date = timezone.now()
            return self.delivered_at + timedelta(days=3) >= current_date
        return False
    
class OrderProduct(models.Model):
    # STATUS = (
    #     ('Nefw','Nefw'),
    #     ('Accepted','Accepted'),
    #     ('Completed','Completed'),
    #     ('Cancelled','Cancelled'),
    #     ('Confirmed','Confirmed'),
    #     ('shipping','shipping'),
    #     ('Delivered','Delivered'),
    #     ('Cancelled','Cancelled'),
    #     ('Return initiated','Return initiated'),
    #     ('Returned','Returned'),
    # )
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name= 'ordered_products')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,blank=True, null=True)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    # order_product_status = models.CharField(max_length=50,choices=STATUS,default='New')
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.product.product_name
    
