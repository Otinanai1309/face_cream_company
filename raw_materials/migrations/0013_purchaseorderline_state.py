# Generated by Django 4.2.13 on 2024-08-01 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0012_purchaseinvoice_purchaseinvoiceline'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderline',
            name='state',
            field=models.CharField(choices=[('pending', 'Pending'), ('partial', 'Partially Fulfilled'), ('fulfilled', 'Fulfilled')], default='pending', max_length=20),
        ),
    ]
