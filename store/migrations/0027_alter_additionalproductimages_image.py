# Generated by Django 5.0 on 2024-01-16 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0026_product_additonal_images_additionalproductimages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalproductimages',
            name='image',
            field=models.ImageField(null=True, upload_to='photos/product-variant/additional-images'),
        ),
    ]