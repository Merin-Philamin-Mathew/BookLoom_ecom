
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=300, blank=True)
    parent_cat = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE)
    is_active = models.BooleanField(default = True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category,self).save(*args, **kwargs)

    # def get_url(self):
    #     return reverse('product_by_category',args=[self.slug])
    

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    
    def __str__(self):
        return self.category_name


#  Create your models here.
""" 
class Attribute(models.Model):
    attribute_name = models.CharField(max_length=150,unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.attribute_name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE,related_name='value')
    attribute_value = models.CharField(max_length=250,unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return str(self.attribute) + "-" + self.attribute_value

class Publication(models.Model):
    name = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name """
    
class Author(models.Model):
    author_name = models.CharField(max_length=50,unique=True)
    about_authour = models.TextField(null = True, blank = True)
    is_active = models.BooleanField(default=True)
    author_created_at = models.DateTimeField(auto_now_add=True)
    author_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author_name


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255,null = True, unique=True)
    short_description = models.CharField(max_length = 255 ,null=True, blank = True)
    long_description = models.TextField(blank=True, null=True)
    #images
    #stock
    #price
    thumbnail_image = models.ImageField(upload_to='photos/product-variant/thumbnail')
    additonal_images = models.ImageField(null=True,upload_to='photos/product-variant/additional_images')
    max_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField()
    #if translated:
        #product_name - translsator - language
    #else:
        #product_name - author
    #translated = models.booleanfield(....)
    #language as attribute if more variants or just put the language in product variant
    author = models.ForeignKey(Author,on_delete=models.CASCADE, related_name = 'writen_books')
    #
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='cat_products')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        product_slug_name = f'{self.product_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(slug__startswith=base_slug).count()
        if counter > 0:
            self.slug = f'{base_slug}-{counter}'
        else:
            self.slug = base_slug
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.product_name
    
""" class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='more_details')
    all_attributes = models.ManyToManyField(AttributeValue,related_name='attributes')
    sku_id = models.IntegerField()
    max_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=6,decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.IntegerField()
    product_variant_slug = models.SlugField(max_length=255,unique=True)
    author = models.ForeignKey(Author,on_delete=models.CASCADE, related_name = 'writen_books')
    publication = models.ForeignKey(Publication,on_delete=models.CASCADE,related_name = "published_books")
    thumbnail_image = models.ImageField(upload_to='photos/product-variant/thumbnail')
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):   #self.product.publication.name 
        product_variant_slug_name = f'{self.publication.name}-{self.product.product_name}-{self.product.category.category_name}-{self.sku_id}'
        base_slug = slugify(product_variant_slug_name)
        counter = ProductVariant.objects.filter(product_variant_slug__startswith=base_slug).count()
        if counter > 0:
            self.product_variant_slug = f'{base_slug}-{counter}'
        else:
            self.product_variant_slug = base_slug
        super(ProductVariant, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('product_variant_detail',args=[self.product.category.slug,self.product_variant_slug])
        

    def get_product_name(self):
        return f'{self.product.product_name}-{self.sku_id} - {", ".join([value[0] for value in self.attribute.all().values_list("attribute_value")])} by {self.product.publication}'

    def __str__(self):
        return self.product_variant_slug
    
class AdditionalProductImages(models.Model):
    product_variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE,related_name='additional_product_images')
    image = models.ImageField(upload_to='photos/product-variant/additional-images')
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.image.url """
    

    

    


        
    