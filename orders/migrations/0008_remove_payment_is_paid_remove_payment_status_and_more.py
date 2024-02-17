# Generated by Django 5.0.1 on 2024-02-17 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_payment_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_signature',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('SUCCESS', 'Success')], default='PENDING', max_length=20),
        ),
    ]
