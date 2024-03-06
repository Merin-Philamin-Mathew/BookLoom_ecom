from django.db import models
from adminapp.models import NewUser 
# Create your models here.
class Wallet(models.Model):
    user    = models.ForeignKey(NewUser, on_delete=models.CASCADE, related_name='wallet' )
    balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + str(self.balance)

class Transaction(models.Model):
    TRANSACTION_CHOICES =(
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
        ("REFERRAL", "Referral"),
        )
    wallet           = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount           = models.IntegerField(default=0)
    transaction_type = models.CharField(choices=TRANSACTION_CHOICES,max_length=10)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_type + str(self.wallet) + str(self.amount)