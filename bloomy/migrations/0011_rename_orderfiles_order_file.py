# Generated by Django 5.0.6 on 2024-06-24 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bloomy', '0010_remove_delivery_comment_delivery_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='orderFiles',
            new_name='file',
        ),
    ]
