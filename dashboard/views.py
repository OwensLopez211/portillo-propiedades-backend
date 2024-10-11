from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from properties.forms import PropertyForm
from properties.models import Property, PropertyImage, Region, Comuna, Agent
from django.db import IntegrityError, transaction
from django.urls import reverse
from cloudinary.uploader import destroy  # Importar función para eliminar imágenes de Cloudinary
import csv

@login_required
def dashboard_view(request):
    total_properties = Property.objects.count()
    context = {
        'total_properties': total_properties,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.created_by = request.user
            property_instance.save()

            # Manejar imágenes
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_instance, image=image)

            return redirect(reverse('dashboard:list-property'))
    else:
        form = PropertyForm()

    return render(request, 'dashboard/add-property.html', {'form': form})

@login_required
def list_property_view(request):
    properties = Property.objects.all()
    return render(request, 'dashboard/list-property.html', {'properties': properties})

@login_required
def edit_property_view(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            property_instance.delete()
            return redirect(reverse('dashboard:list-property'))

        # Procesar el formulario de la propiedad
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            property_instance = form.save()

            # Manejar la carga de nuevas imágenes
            if request.FILES.getlist('images'):
                for image_file in request.FILES.getlist('images'):
                    PropertyImage.objects.create(property=property_instance, image=image_file)

            return redirect(reverse('dashboard:edit-property', args=[property_id]))
    else:
        form = PropertyForm(instance=property_instance)

    # Obtener todas las imágenes relacionadas con la propiedad
    images = PropertyImage.objects.filter(property=property_instance)

    return render(request, 'dashboard/edit-property.html', {
        'form': form,
        'property': property_instance,
        'images': images,
    })

@login_required
def delete_property_image(request, property_id, image_id):
    property_instance = get_object_or_404(Property, id=property_id)
    image_instance = get_object_or_404(PropertyImage, id=image_id, property=property_instance)
    try:
        image_instance.delete()
        print(f"Deleted image with ID: {image_id}")
    except Exception as e:
        print(f"Error deleting image: {e}")
    return redirect(reverse('dashboard:edit-property', args=[property_id]))



@login_required
def delete_property_view(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Primero, elimina las imágenes asociadas
                images = PropertyImage.objects.filter(property=property_instance)
                for image in images:
                    # Eliminar la imagen de Cloudinary usando el public_id
                    if image.image:
                        print(f"Eliminando imagen: {image.image.public_id}")  # Mensaje de depuración
                        destroy(image.image.public_id)  # Elimina la imagen de Cloudinary
                    # Eliminar el objeto de imagen de la base de datos
                    image.delete()
                
                # Luego, elimina la propiedad
                property_instance.delete()
                messages.success(request, "Propiedad eliminada con éxito.")
        except IntegrityError:
            messages.error(request, "No se pudo eliminar la propiedad debido a una restricción de clave externa.")
        
        return redirect(reverse('dashboard:list-property'))

    return redirect(reverse('dashboard:edit-property', args=[property_id]))


@login_required
def feature_property_view(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        is_featured = request.POST.get('is_featured') == 'on'
        property_instance = Property.objects.get(id=property_id)
        property_instance.is_featured = is_featured
        property_instance.save()
        return redirect(reverse('dashboard:list-property'))

    properties = Property.objects.all()
    return render(request, 'dashboard/feature-property.html', {'properties': properties})

@login_required
def upload_properties(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        
        # Validar que el archivo sea un CSV
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Por favor, sube un archivo CSV válido.')
            return redirect(reverse('dashboard:upload-properties'))

        try:
            file_data = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(file_data)

            # Saltar encabezado
            next(reader, None)

            for row in reader:
                try:
                    # Validar longitud de la fila
                    if len(row) < 14:
                        messages.error(request, f'Error al procesar la fila: {row}. Detalles: Fila incompleta.')
                        continue

                    # Buscar la instancia de la región
                    region_nombre = row[5]
                    try:
                        region_instance = Region.objects.get(nombre=region_nombre)
                    except Region.DoesNotExist:
                        messages.error(request, f'Error al procesar la fila: {row}. Detalles: La región "{region_nombre}" no existe.')
                        continue

                    # Buscar la instancia de la comuna
                    comuna_nombre = row[6]
                    try:
                        comuna_instance = Comuna.objects.get(nombre=comuna_nombre, region=region_instance)
                    except Comuna.DoesNotExist:
                        messages.error(request, f'Error al procesar la fila: {row}. Detalles: La comuna "{comuna_nombre}" no existe en la región "{region_nombre}".')
                        continue

                    # Parsear los campos numéricos
                    precio_venta = float(row[7]) if row[7] else None
                    precio_renta = float(row[8]) if row[8] else None
                    habitaciones = int(row[9]) if row[9] else None
                    baños = int(row[10]) if row[10] else None
                    gastos_comunes = float(row[11]) if row[11] else None
                    contribuciones = float(row[12]) if row[12] else None

                    # Validar existencia del agente
                    agent_id = row[13]
                    try:
                        agent_instance = Agent.objects.get(id=agent_id)
                    except Agent.DoesNotExist:
                        messages.error(request, f'Error al procesar la fila: {row}. Detalles: El agente con ID "{agent_id}" no existe.')
                        continue

                    # Crear la propiedad
                    Property.objects.create(
                        title=row[0],
                        tipo_operacion=row[1],
                        tipo_propiedad=row[2],
                        descripcion=row[3],
                        direccion=row[4],
                        region=region_instance,
                        comuna=comuna_instance,
                        precio_venta=precio_venta,
                        precio_renta=precio_renta,
                        habitaciones=habitaciones,
                        baños=baños,
                        gastos_comunes=gastos_comunes,
                        contribuciones=contribuciones,
                        agent=agent_instance
                    )
                except Exception as e:
                    messages.error(request, f'Error al procesar la fila: {row}. Detalles: {str(e)}')
                    continue

            messages.success(request, 'Propiedades subidas exitosamente.')
            return redirect(reverse('dashboard:upload-properties'))

        except UnicodeDecodeError as e:
            messages.error(request, f'Error al leer el archivo CSV. Detalles: {str(e)}')
            return redirect(reverse('dashboard:upload-properties'))

    return render(request, 'dashboard/upload_properties.html')
