from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'admin_app'

urlpatterns = [
    path('login/',views.admin_login,name='admin_login'),
    path('logout/',views.admin_logout,name='admin_logout'),
    
    path('',views.admin_dashboard,name='admin_dashboard'),
    path('sales-report-pdf/', views.SalesReportPDFView.as_view(), name='sales_report_pdf'),

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

    path('addproductvariant/<str:slug>',views.addproductvariant,name='add_product_variant'),
    #category management____________________________________________________________
    path('category',views.listcategory,name='category'),
    path('addcategory',views.addcategory,name='add_category'),
    path('editcategory/<str:slug>',views.editcategory,name='edit_category'),
    path('controlcategory/<str:slug>',views.controlcategory,name='control_category'),
     
    #author management____________________________________________________________
    path('listauthor',views.listauthor,name='list_author'),
    path('addauthor',views.addauthor,name='add_author'),
    path('editauthor/<slug:slug>',views.editauthor,name='edit_author'),
    path('controlauthor/<str:slug>',views.controlauthor,name='control_author'),
     
    #publication management____________________________________________________________
    path('listpublication',views.listpublication,name='list_publication'),
    path('addpublication',views.addpublication,name='add_publication'),
    path('editpublication/<int:id>',views.editpublication,name='edit_publication'),
    path('controlpublication/<int:id>',views.controlpublication,name='control_publication'),

    #language management____________________________________________________________
    path('listlanguage',views.listlanguage,name='list_language'),
    path('addlanguage',views.addlanguage,name='add_language'),
    path('editlanguage/<int:id>',views.editlanguage,name='edit_language'),
    path('controllanguage/<int:id>',views.controllanguage,name='control_language'),
   
    #order management____________________________________________________________
    path('listorder',views.listorder,name='list_order'),
    path('change-order-status/<int:id>/', views.change_order_status, name='change_order_status'),

    #coupon management____________________________________________________________
    path('coupons', views.coupons, name='coupons'),
    # path('add_coupons', views.add_coupons, name='add_coupons'),
    path('edit_coupons', views.edit_coupons, name='edit_coupons'),
    path('activate_coupon/<int:id>/', views.activate_coupon, name='activate_coupon'),
    path('disable_coupon/<int:id>/', views.disable_coupon, name='disable_coupon'),
    


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

