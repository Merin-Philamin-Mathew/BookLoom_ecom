from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
#from django_otp.models import TimeBasedOTP
# Create your models here.

#imported in adminapp.admin homeapp.views
class NewUser(AbstractUser):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
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
        return self.username
    

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