from django.db import models
from accounts.models import *
from product.models import *


# Create your models here.

class OrderAddress(models.Model):
    name = models.CharField(max_length=50, null=False)
    house_name = models.CharField(max_length=500, null=False)
    street_name = models.CharField(max_length=500, null=False)
    pin_number = models.IntegerField(null=False)
    district = models.CharField(max_length=300, null=False)
    state = models.CharField(max_length=300, null=False)
    country = models.CharField(max_length=50, null=False, default="null")
    phone_number = models.CharField(max_length=50, null=False)


class OrderMain(models.Model):
    user = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL, null=True)
    total_amount = models.FloatField(null=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    final_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    date = models.DateField(auto_now_add=True)
    order_status = models.CharField( max_length=100, default="Order Placed")
    payment_option = models.CharField(max_length=100, default="Cash_on_delivery")
    order_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50)
    reason=models.CharField(max_length=500,null=True)
    updated_at = models.DateTimeField(auto_now=True)  
    



class OrderSub(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    main_order = models.ForeignKey(OrderMain, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    price = models.FloatField(null=False, default=0)
    quantity = models.IntegerField(null=False, default=0)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, null=True,blank=True)
    
    def total_cost(self):
       return self.quantity * self.price
    def final_total_cost(self):
        return self.quantity * self.price
    

class ReturnRequest(models.Model):
    RETURN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    order_main = models.ForeignKey(OrderMain, on_delete=models.CASCADE, null=True,blank=True)
    order_sub = models.ForeignKey(OrderSub, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 



class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateField(auto_now_add=True) 
    

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type=models.CharField(max_length=500)         
       