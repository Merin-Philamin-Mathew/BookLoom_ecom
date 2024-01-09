from django import forms
from django.contrib.auth.forms import UserCreationForm
from adminapp.models import NewUser
from phonenumber_field.modelfields import PhoneNumberField
#pip install babel
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    #i tried to do the phonenumberfield didnt work as i typed forms.phonenumberfield 
    #phone_number field is not a part of forms uses forms.charfield
    #hence import phonenumberPrefixWidgets for placeholder 
    phone_number = forms.CharField(widget=PhoneNumberPrefixWidget(attrs={"placeholder": "Phone Number"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password"}))

    class Meta:
        model = NewUser
        fields = ['username','email','phone_number',]

       
"""     def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        try:
            # Attempt to validate the phone number
            PhoneNumberField().clean(phone_number)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
        return phone_number
     """

