from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'admin_app'

urlpatterns = [
    path('admin/',views.admin_login,name='admin_login'),
    path('dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('adminlogout/',views.admin_logout,name='admin_logout'),

    #user management_________________________________________________________________
    path('userinfo',views.userinfo,name='userinfo'),
    path('adduser',views.adduser,name='adduser'),
    path('edituser/<pk>',views.edituser,name='edituser'),
    #path('deleteuser/<pk>',views.deleteuser,name='deleteuser'),
    path('usercontrol/,<int:user_id>',views.controluser,name='control_user'),
    
    #product management_____________________________________________________________
    path('listproducts',views.listproducts,name='list_products'),
    path('addproducts',views.addproducts,name='add_products'),
    path('editproducts/<str:slug>',views.editproducts,name='edit_products'),
    path('controlproducts/<str:slug>',views.controlproducts,name='control_products'),

    #category management____________________________________________________________
    path('category',views.listcategory,name='category'),
    path('addcategory',views.addcategory,name='add_category'),
    path('editcategory/<str:slug>',views.editcategory,name='edit_category'),
    path('controlcategory/<str:slug>',views.controlcategory,name='control_category'),
     
    #author management____________________________________________________________
    path('author',views.listauthor,name='author'),
    path('addauthor',views.addauthor,name='add_author'),
    path('editauthor/<str:slug>',views.editauthor,name='edit_author'),
    path('controlauthor/<str:slug>',views.controlauthor,name='control_author'),
     
    #publication management____________________________________________________________
    path('publication',views.listpublication,name='publication'),
    path('addpublication',views.addpublication,name='add_publication'),
    path('editpublication/<str:slug>',views.editpublication,name='edit_publication'),
    path('controlpublication/<str:slug>',views.controlpublication,name='control_publication'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

