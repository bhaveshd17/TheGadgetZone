# Generated by Django 3.1.7 on 2021-04-03 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_auto_20210403_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discountPrice',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
        migrations.AlterField(
            model_name='product',
            name='savePrice',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
    ]