# Generated by Django 5.0.6 on 2024-07-25 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bloomy', '0002_subscription_stripe_session_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specification',
            name='delivery_format',
        ),
        migrations.RemoveField(
            model_name='specification',
            name='pixel_size',
        ),
        migrations.AddField(
            model_name='order',
            name='pixel_size',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
