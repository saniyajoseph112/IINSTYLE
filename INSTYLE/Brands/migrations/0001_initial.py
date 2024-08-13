# Generated by Django 5.0.7 on 2024-08-01 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=30)),
                ('brand_image', models.ImageField(upload_to='brand_image/')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]