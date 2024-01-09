from django.contrib import admin
from . models import Category, Product, Author

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug', 'description', 'parent_cat')


class ProductAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ('product_name', 'author', 'category', 'is_available')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
#admin.site.register(ProductVariant)
#admin.site.register(Attribute)
#admin.site.register(AttributeValue)
#admin.site.register(Publication)
admin.site.register(Author)
#admin.site.register(AdditionalProductImages)