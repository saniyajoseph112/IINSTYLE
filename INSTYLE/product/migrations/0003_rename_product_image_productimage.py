# Generated by Django 5.0.7 on 2024-08-06 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_delete_product_variant_images'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='product_image',
            new_name='ProductImage',
        ),
    ]
