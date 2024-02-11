from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
#from django_otp.models import TimeBasedOTP
# Create your models here.

#overriding the abstractuser
#imported in adminapp.admin homeapp.views

class NewUser(AbstractUser):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
        ('unblocked', 'Unblocked'),
    ]
    user_id = models.BigAutoField(primary_key=True, unique=True,)
    email = models.EmailField(_("Email Address"), unique = True,)
    username = models.CharField(max_length = 100)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',  # Default value if not provided
    )

    phone_number = PhoneNumberField(unique = True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username','phone_number']

    # def verify_otp(self, otp):
    #     return self.verify_otp_value(otp)

    def __str__(self):
        return self.email
    
    

    
def upload_path(instance, filename):
    # Get the username of the associated user
    username = instance.user.username

    # Construct the upload path
    upload_path = f'profile-pic/user/{username}/{filename}' 
    return upload_path

#--------------------------user page----------------------------
#-------------------------user details--------------------------
class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=30,null = True)
    last_name = models.CharField(max_length=30,null = True)
    profile_image = models.ImageField(null=True, blank=True, upload_to=upload_path)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)

    def __str__(self):
        return self.user.username

class Addresses(models.Model):
    COUNTRY_CHOICES = [('IN', 'India')]  # Add more countries if needed
    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
    ]
    user = models.ForeignKey(NewUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='IN')
    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)    
    
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Addresses.objects.filter(user = self.user).exclude(pk=self.pk).update(is_default=False)
        super(Addresses, self).save(*args, **kwargs)
        
    def get_user_full_address(self):
        address_parts = f"{self.name}, {self.phone_number}, {self.address_line_1}"
        
        if self.address_line_2:
            address_parts += (', '+self.address_line_2)
        
        address_parts += (f", Pin: {self.pincode}, {self.city}, {self.state}, {self.country}")
        
        
        return address_parts
        # return f'{self.name},{self.phone},Pin:{self.pincode},Address:{self.address_line_1},{self.address_line_2},{self.city},{self.state},{self.country}'
    
    def __str__(self):
        return self.name    

""" 
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.core.mail import send_mail
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)


@receiver(post_save, sender = NewUser)
def send_email(sender, instance, created, **kwargs):
    try:
        if created:
            
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance, email_token = email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
            # subject = 'Account Activation'
            # message = f'Your account activation token is: {email_token}'
            # from_email = 'vssadique785@gmail.com'  
            # to_email = [email]
            
            # # Send email
            # send_mail(subject, message, from_email, to_email)

    except Exception as e:
        print(e) 


from django.conf import settings
from django.core.mail import send_mail


def send_account_activation_email(email, email_token):
    subject = "Your account need to be verified"
    email_from = settings.EMAIL_HOST_USER
    message = f"Hi, click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}"
    print(message)
    

    send_mail(subject, message, email_from, [email])
 """

