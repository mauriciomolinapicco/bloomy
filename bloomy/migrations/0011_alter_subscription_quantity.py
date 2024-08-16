# Generated by Django 5.0.6 on 2024-08-16 12:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bloomy', '0010_subscription_quantity_alter_order_for_peca_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='quantity',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
    ]
