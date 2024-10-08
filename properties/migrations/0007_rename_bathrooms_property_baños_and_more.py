# Generated by Django 5.1 on 2024-08-30 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_property_comuna_property_region_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='bathrooms',
            new_name='baños',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='common_expenses',
            new_name='contribuciones',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='description',
            new_name='descripcion',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='address',
            new_name='direccion',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='contributions',
            new_name='gastos_comunes',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='bedrooms',
            new_name='habitaciones',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='rent_price',
            new_name='precio_renta',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='sale_price',
            new_name='precio_venta',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='created_at',
            new_name='publicada',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='property_type',
            new_name='tipo_propiedad',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='title',
            new_name='titulo',
        ),
        migrations.AddField(
            model_name='property',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='property_images/'),
        ),
    ]
