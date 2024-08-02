# Generated by Django 4.2.13 on 2024-08-01 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0013_purchaseorderline_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderline',
            name='invoiced_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]