# Generated by Django 5.0 on 2024-01-16 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_additionalproductimages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='publication_date',
        ),
    ]
