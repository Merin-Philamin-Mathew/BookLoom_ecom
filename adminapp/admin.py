from django.contrib import admin
from . models import NewUser,Profile,Addresses,Coupon,Verify_coupon

# Register your models here.

class CustomAdmin(admin.ModelAdmin):
    list_display = ['username','email','phone_number','status']
    list_filter = ('status',)
    search_fields=('username','email','phone_number')
    """ actions = ['block_users','unblock_users']

    def block_users(self, request, querset):
        querset.update(status = 'blocked')
    def unblock_users(self, request, queryset):
        queryset.update(status='unblocked')

    block_users.short_description = 'Block selected users'
    unblock_users.short_description = 'Unblock selected users' """
    model = NewUser
                    #User    #UserAdmin
admin.site.register(NewUser, CustomAdmin)
admin.site.register(Profile)
admin.site.register(Addresses)
admin.site.register(Coupon)
admin.site.register(Verify_coupon)



