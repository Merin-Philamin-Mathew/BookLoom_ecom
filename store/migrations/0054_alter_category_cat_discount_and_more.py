# Generated by Django 5.0.1 on 2024-02-14 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0053_remove_productvariant_sale_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='cat_discount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='pro_discount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]