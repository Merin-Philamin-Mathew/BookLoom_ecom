# Generated by Django 5.0 on 2024-01-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_remove_publication_publication_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='author_image',
            field=models.ImageField(null=True, upload_to='photos/profile-pic/author'),
        ),
    ]
