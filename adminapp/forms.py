from django import forms
from . models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model=Coupon
        fields = ['discount','code','max_discount','min_amount','active','uses','active_date','expiry_date']
        widgets = {
            'discount': forms.NumberInput(attrs={'class': 'form-control mb-3',"placeholder": "Discount"}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control mb-3',"placeholder": "Max-Discount"}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control mb-3', "placeholder": "Min-amount"}),
            'uses': forms.NumberInput(attrs={'class': 'form-control mb-3', "placeholder": "Uses"}),
            'code': forms.TextInput(attrs={'class': 'form-control mb-3', "placeholder": "Code"}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'active_date': forms.DateInput(attrs={'type': 'date','class': 'form-control mb-3'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date','class': 'form-control mb-3'})
        }