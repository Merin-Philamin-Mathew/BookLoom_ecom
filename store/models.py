from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    category_name = models.CharField(max_length=255, unique=True)
    parent = models.CharField(max_length=255,null=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=255,blank = True, unique=True)
    description = models.TextField(max_length=500,blank=True)
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now = True)

"""     def save(self, *args, **kwargs):
        product_slug_name = f'{self.publication.name}-{self.product_name}-{self.category.category_name}'
        base_slug = slugify(product_slug_name)
        counter = Product.objects.filter(slug__startswith=base_slug).count()
        if counter > 0:
            self.slug = f'{base_slug}-{counter}'
        else:
            self.slug = base_slug
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name """
        
    