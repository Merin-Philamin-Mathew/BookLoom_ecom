# Generated by Django 5.0.1 on 2024-02-17 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_razor_pay_order_id_order_razor_pay_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]
