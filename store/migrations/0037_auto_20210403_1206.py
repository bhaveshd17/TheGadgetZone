# Generated by Django 3.1.7 on 2021-04-03 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_review_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
