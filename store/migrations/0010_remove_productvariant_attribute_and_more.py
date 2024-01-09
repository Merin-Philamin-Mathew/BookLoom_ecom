# Generated by Django 5.0 on 2024-01-08 05:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_product_description_author_about_authour_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='attribute',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='author',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='publication',
        ),
        migrations.AlterField(
            model_name='attributevalue',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='value', to='store.attribute'),
        ),
        migrations.DeleteModel(
            name='AdditionalProductImages',
        ),
        migrations.DeleteModel(
            name='ProductVariant',
        ),
    ]
