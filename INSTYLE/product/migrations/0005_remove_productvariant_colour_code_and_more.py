# Generated by Django 5.0.7 on 2024-08-08 04:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_rename_product_variant_productvariant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='colour_code',
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='colour_name',
        ),
    ]
