# Generated by Django 5.0.1 on 2024-03-06 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_shipping_addresses_order_shipping_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='wallet_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50, null=True),
        ),
    ]
