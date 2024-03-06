from django import forms
from django.contrib.auth.forms import UserCreationForm
from adminapp.models import NewUser,Profile,Addresses
from phonenumber_field.modelfields import PhoneNumberField
#pip install babel
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator,MinLengthValidator

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

    

class ProfileForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'date_of_birth':
                field.widget.attrs['placeholder'] = 'YYYY-MM-DD'

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']


def validate_phone_number(value):
    if not value.strip().isdigit():
        raise ValidationError("Phone number should only contain digits.")
    if len(value.strip()) != 10:
        raise ValidationError("Phone number must be exactly 10 digits.")
    if value.strip().startswith('0'):
        raise ValidationError("Phone number should not start with '0'.")

class AddressForm(forms.ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'phone_number':
                field.validators.append(MaxLengthValidator(limit_value=10, message="Phone number must be exactly 10 digits."))
                field.validators.append(validate_phone_number)
        
    class Meta:
        model = Addresses
        exclude = ('user','is_default','is_active')  


       
"""     def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        try:
            # Attempt to validate the phone number
            PhoneNumberField().clean(phone_number)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
        return phone_number
     """

