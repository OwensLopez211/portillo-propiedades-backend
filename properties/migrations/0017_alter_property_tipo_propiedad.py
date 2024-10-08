# Generated by Django 5.1 on 2024-09-02 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0016_property_tipo_operacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='tipo_propiedad',
            field=models.CharField(choices=[('casa', 'Casa'), ('departamento', 'Departamento'), ('oficina', 'Oficina'), ('comercial', 'Comercial'), ('parcela', 'Parcela'), ('estacionamiento', 'Estacionamiento'), ('bodega', 'Bodega'), ('terreno', 'Terreno')], default='house', max_length=20),
        ),
    ]
