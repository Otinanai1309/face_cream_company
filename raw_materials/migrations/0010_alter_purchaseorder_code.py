# Generated by Django 4.2.13 on 2024-07-23 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0009_alter_rawmaterial_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='code',
            field=models.CharField(max_length=20),
        ),
    ]
