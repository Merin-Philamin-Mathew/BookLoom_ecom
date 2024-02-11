from django.contrib import admin
from . models import Category, Product, ProductVariant, Author, Publication, Language, AdditionalProductImages

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug', 'parent_cat')

class AdditionalProductImagesAdmin(admin.StackedInline):
    model = AdditionalProductImages

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_variant_slug', )
    inlines = [AdditionalProductImagesAdmin]
    
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ('product_name', 'author', 'category', 'is_available')

class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('author_name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant,ProductVariantAdmin)
admin.site.register(Publication)
admin.site.register(Language)
admin.site.register(Author,AuthorAdmin)
admin.site.register(AdditionalProductImages)