from django.contrib import admin
from . models import NewUser

# Register your models here.

class CustomAdmin(admin.ModelAdmin):
    list_display = ['username','email','status','phone_number']
    model = NewUser
                    #User    #UserAdmin
admin.site.register(NewUser, CustomAdmin)



