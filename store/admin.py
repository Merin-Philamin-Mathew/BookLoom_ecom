from django.contrib import admin
from . models import Category, Product, ProductVariant, Attribute, AttributeValue, Publication, Author, AdditionalProductImages

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug', 'description', 'parent_cat')

admin.site.register(Category, CategoryAdmin)


admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(Publication)
admin.site.register(Author)
admin.site.register(AdditionalProductImages)