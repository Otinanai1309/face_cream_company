# Generated by Django 4.2.13 on 2024-08-24 08:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0018_purchaseinvoice_stock_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseinvoice',
            name='stock_updated',
        ),
    ]
