# Generated by Django 4.2.13 on 2024-07-07 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateField(auto_now_add=True)),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raw_materials.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('vat', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raw_materials.order')),
                ('raw_material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raw_materials.rawmaterial')),
            ],
        ),
    ]
