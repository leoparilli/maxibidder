import os
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
#Improtar los modelos
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Prefetch
from .models import CarMake, CarModel, Photo, Video, Vehicle, Carousel
from django.contrib  import messages
from django.core.paginator import Paginator
#from .forms import UserForm, ClientRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied  # <-- Agrega este import
from django.utils.safestring import mark_safe
from smtplib import SMTPException
from django.contrib.auth import update_session_auth_hash  # <-- Agrega este import
from django.contrib.auth import views as auth_views
from django.contrib import messages
from math import ceil

# Agrega esta función al inicio
def is_admin(user):
    return user.is_authenticated and user.profile.role == 'Admin'


# Create your views here.
#MANEJO DE ERRORES 403 Y CRSF   13/02/2025
def handler403(request, exception=None):
    return render(request, '403.html', status=403)

def csrf_failure(request, reason=""):
    return render(request, 'gestioncar/403_csrf.html', status=403)

#VISTA LOGIN


# VISTA CONTACTO
def contact_us(request):
    return render(request, 'gestioncar/contact_us.html')



#VISTA HOME.



def  home(request):
    random_vehicles = Vehicle.objects.order_by('?')[:10]  # 10 random vehicles
    carousels = Carousel.objects.filter(is_active=True).order_by('order')  # Slides activos del carrusel
    return render(request, 'gestioncar/home.html', {
        'random_vehicles': random_vehicles,
        'carousels': carousels  # Agrega los slides del carrusel al contexto
    })

def  inventory(request):
    from django.db.models import Prefetch

#----------------------- Inventory---------------------------------------------
def inventory(request):
    search_query = request.GET.get('search', '')
    make_filter = request.GET.get('make', '')
    year_filter = request.GET.get('year', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    vehicles = Vehicle.objects.select_related('make', 'car_model').prefetch_related(
        Prefetch('fotos', queryset=Photo.objects.all()[:1], to_attr='primary_photo')
    ).order_by('-date_add')

    # Filtros
    if search_query:
        vehicles = vehicles.filter(stock__icontains=search_query)
    if make_filter:
        vehicles = vehicles.filter(make__make__iexact=make_filter)
    if year_filter:
        vehicles = vehicles.filter(year=year_filter)
    if price_min:
        vehicles = vehicles.filter(price__gte=price_min)
    if price_max:
        vehicles = vehicles.filter(price__lte=price_max)

    # Para los dropdowns de filtros
    makes = CarMake.objects.all()
    years = Vehicle.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'vehicles': vehicles,
        'makes': makes,
        'years': years,
        'search_query': search_query,
        'selected_make': make_filter,
        'selected_year': year_filter,
        'price_min': price_min or '',
        'price_max': price_max or '',
    }
    paginator = Paginator(vehicles, 12)  # 12 items por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    return render(request, 'gestioncar/inventory.html', context)
    #return  render(request, 'gestioncar/inventory.html')#HttpResponse("Inventory")

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle.objects.select_related('make', 'car_model')
                                .prefetch_related('fotos', 'videos'), 
                                pk=pk)
    return render(request, 'gestioncar/vehicle_detail.html', {'vehicle': vehicle})



def  car_finder(request):
    return  render(request, 'gestioncar/car_finder.html')#HttpResponse("Car_Finder")

def  buy_with_us(request):
    return  render(request, 'gestioncar/buy_with_us.html')#HttpResponse("Buy_With_Us")

def  about_us(request):
    return  render(request, 'gestioncar/about_us.html')#HttpResponse("About_Us")

def  my_account(request):
    #return  render(request, 'gestioncar/my_account.html')#HttpResponse("My_Account")
    return redirect('edit_client', id=request.user.id)

def  admin_maxibidder(request):
    return  render(request, 'gestioncar/admin_maxibidder.html')#HttpResponse("Admin_Maxibidder")

#----------VISTA COMPARE --------------------------------------------------
def compare(request):
    # Vehículo principal seleccionado
    selected_vehicle_id = request.GET.get('selected_vehicle')
    selected_vehicle = get_object_or_404(Vehicle, id=selected_vehicle_id) if selected_vehicle_id else None

    # Vehículo para comparar
    compare_with_id = request.GET.get('compare_with')
    compare_with_vehicle = get_object_or_404(Vehicle, id=compare_with_id) if compare_with_id else None

    # Filtros
    make_filter = request.GET.get('make')
    model_filter = request.GET.get('model')
    year_filter = request.GET.get('year')

    # Query
    comparable_vehicles = Vehicle.objects.exclude(id=selected_vehicle_id) if selected_vehicle_id else Vehicle.objects.all()

    if make_filter:
        comparable_vehicles = comparable_vehicles.filter(make__make__iexact=make_filter)
    if model_filter:
        comparable_vehicles = comparable_vehicles.filter(car_model__model_make__iexact=model_filter)
    if year_filter:
        comparable_vehicles = comparable_vehicles.filter(year=year_filter)

    context = {
        'selected_vehicle': selected_vehicle,
        'compare_with_vehicle': compare_with_vehicle,
        'comparable_vehicles': comparable_vehicles.prefetch_related('fotos'),
        'makes': CarMake.objects.all(),
        'models': CarModel.objects.values_list('model_make', flat=True).distinct(),
        'years': Vehicle.objects.values_list('year', flat=True).distinct().order_by('-year'),
        'make_filter': make_filter,
        'model_filter': model_filter,
        'year_filter': year_filter,
    }
    return render(request, 'gestioncar/compare.html', context)



#---------------------------------CRUD BRAND
@login_required
def make(request):
    makelist=CarMake.objects.all()  #consultar todas las marcas
    return render(request, 'gestioncar/make.html', {"make":makelist})

@login_required
def register_brand(request):
    if request.method == 'POST':
        brand = request.POST["txtbrand"].strip()  #nombre como se llamo en el html txtbrand, strip() # Obtener y limpiar el nombre de la marca
        if CarMake.objects.filter(make__iexact=brand).exists():  # Verificar si la marca ya existe (sin importar mayúsculas/minúsculas)
            messages.error(request, 'The brand already exists. Please enter a different brand.')
        else:
            b=CarMake(make=brand)   #lo del lado izquierdo es como se llama en el modelo y lo del derecho es como llame a la variable
            b.save()
            messages.success(request,'Brand added successfully!')
    return redirect ('Make')

@login_required
def delete_brand(request, id):
    #brand = get_object_or_404(Brand, id=id)
    brand = CarMake.objects.filter(pk=id)
    brand.delete()
    messages.success(request, 'Brand delete  successfully!')
    return redirect('Make')  # Redirige al url adecuado en  mi caso Make mayuscula porque en models.py esta en mayuscula


@login_required
def brand_detail(request, id):
    brand = CarMake.objects.get(pk=id)
    return render(request, 'gestioncar/brandedit.html', {'brand' : brand})

@login_required
def brandedit(request):
    if request.method == 'POST':
        id = request.POST["id"]  # Asegúrate de que este campo exista
        make = request.POST["txtbrand"].strip()  # Cambia "make" por "txtbrand"
        CarMake.objects.filter(pk=id).update(make=make)
        messages.success(request, 'Brand updated successfully!')
        return redirect('Make')
    


#--------------------CRUD Brand -- MODEL--------------------------------------------------------------------------
@login_required
def a_model(request):
    modelbrand_list=CarModel.objects.all()
    brands = CarMake.objects.all()  # Obtener todas las marcas
    return render(request, 'gestioncar/a_model.html', {"a_model": modelbrand_list, "brands": brands})
    #return render(request, 'gestioncar/a_model.html', {"a_model":modelbrand_list})

@login_required
def register_model(request):
    if request.method == 'POST':
        brand_id = request.POST["make"]
        model_make = request.POST["txtmodel"].strip()
        
        if CarModel.objects.filter(make_id=brand_id, model_make=model_make).exists():
            messages.error(request, 'The model already exists for this brand.')
        else:
            brand = CarMake.objects.get(pk=brand_id)
            CarModel.objects.create(make=brand, model_make=model_make)
            messages.success(request, 'Model added successfully!')
    return redirect('Model')


@login_required
def delete_model(request, id):
    model = CarModel.objects.get(pk=id)
    model.delete()
    messages.success(request, 'Model deleted successfully!')
    return redirect('Model')

@login_required
def modeledit(request):
    if request.method == 'POST':
        id = request.POST["id"]
        brand_id = request.POST["make"]
        model_make = request.POST["txtmodel"].strip()
        
        brand = CarMake.objects.get(pk=brand_id)
        CarModel.objects.filter(pk=id).update(make=brand, model_make=model_make)
        messages.success(request, 'Model updated successfully!')
        return redirect('Model')
    
@login_required
def model_detail(request, id):
    model = CarModel.objects.get(pk=id)
    brands = CarMake.objects.all()  # Obtener todas las marcas
    return render(request, 'gestioncar/model_detail.html', {'model': model, 'brands': brands})


#-------------CRUD VEHICLE  CAR ---------------------------------------------------------

from .models import CarMake, CarModel, Photo, Video, Vehicle, TITLE_CHOICES, VEHICLE_TYPE_CHOICES, TRANSMISSION_CHOICES
@login_required
def car(request):
    if request.method == 'POST':
        date_add = request.POST.get('date_add')
        stock = request.POST.get('stock')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        make_id = request.POST.get('marca')
        model_id = request.POST.get('modelo')
        title_condition = request.POST.get('title_condition')
        vehicle_type = request.POST.get('vehicle_type')
        transmission = request.POST.get('transmission')
        price = request.POST.get('price').replace('$', '').replace(',', '')
        details = request.POST.get('details')
        foto_principal = request.FILES.get('foto_principal')
        links = request.POST.get('links')

        make = CarMake.objects.get(pk=make_id)
        model = CarModel.objects.get(pk=model_id)

        vehicle = Vehicle(
            date_add=date_add,
            stock=stock,
            year=year,
            mileage=mileage,
            make=make,
            car_model=model,
            title_condition=title_condition,
            vehicle_type=vehicle_type,
            transmission=transmission,
            price=price,
            details=details,
            foto_principal=foto_principal,
            links=links
        )
        
        vehicle.save()

        # Agregar fotos
        fotos = request.FILES.getlist('fotos')
        for foto in fotos:
            photo = Photo(photo=foto)
            photo.save()
            vehicle.fotos.add(photo)

        # Agregar videos
        videos = request.FILES.getlist('videos')
        for video in videos:
            video_obj = Video(video_file=video)
            video_obj.save()
            vehicle.videos.add(video_obj)

        messages.success(request, 'Vehicle added successfully!')
        return redirect('Car')

    # Para la petición GET
    car_makes = CarMake.objects.all()
    car_models = CarModel.objects.all()
    vehicles = Vehicle.objects.all()  # Obtener todos los vehículos listado aca


    return render(request, 'gestioncar/car.html', {
        'marcas': car_makes,
        'modelos': car_models,
        'title_conditions': TITLE_CHOICES,
        'vehicle_types': VEHICLE_TYPE_CHOICES,
        'transmission_types': TRANSMISSION_CHOICES,
        'vehicles': vehicles,  # Pasar la lista de vehículos al template 
    })


@login_required
def get_models(request, make_id):
    models = CarModel.objects.filter(make_id=make_id).values('id', 'model_make')
    return JsonResponse(list(models), safe=False)

@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, pk=id)

    # Eliminar la foto principal
    if vehicle.foto_principal:
        vehicle.foto_principal.delete(save=False)

    # Eliminar todas las fotos relacionadas
    for photo in vehicle.fotos.all():
        photo.photo.delete(save=False)  # Eliminar el archivo físico
        photo.delete()  # Eliminar el registro de la base de datos

    # Eliminar todos los videos relacionados
    for video in vehicle.videos.all():
        video.video_file.delete(save=False)  # Eliminar el archivo físico
        video.delete()  # Eliminar el registro de la base de datos

    # Finalmente, eliminar el vehículo
    vehicle.delete()

    messages.success(request, 'Vehicle and associated files deleted successfully!')
    return redirect('Car')

@login_required
def edit_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, pk=id)

    if request.method == 'POST':
        # Procesar el formulario de edición
        vehicle.date_add = request.POST.get('date_add')
        vehicle.stock = request.POST.get('stock')
        vehicle.year = request.POST.get('year')
        vehicle.mileage = request.POST.get('mileage')
        vehicle.make_id = request.POST.get('marca')
        vehicle.car_model_id = request.POST.get('modelo')
        vehicle.title_condition = request.POST.get('title_condition')
        vehicle.vehicle_type = request.POST.get('vehicle_type')
        vehicle.transmission = request.POST.get('transmission')
        vehicle.price = request.POST.get('price').replace('$', '').replace(',', '')
        vehicle.details = request.POST.get('details')
        vehicle.links = request.POST.get('links')

        # Eliminar la foto principal si se marca el campo oculto
        if 'delete_foto_principal' in request.POST and request.POST['delete_foto_principal'] == '1':
            if vehicle.foto_principal:
                vehicle.foto_principal.delete(save=False)  # Eliminar el archivo físico
                vehicle.foto_principal = None  # Eliminar la referencia en el modelo

        # Actualizar la foto principal si se proporciona una nueva
        if 'foto_principal' in request.FILES:
            if vehicle.foto_principal:  # Eliminar la foto principal anterior
                vehicle.foto_principal.delete(save=False)
            vehicle.foto_principal = request.FILES['foto_principal']

        # Eliminar fotos seleccionadas
        photo_ids = request.POST.getlist('delete_photos')
        for photo_id in photo_ids:
            if photo_id:  # Ignorar campos vacíos
                try:
                    photo = Photo.objects.get(id=photo_id)
                    photo.photo.delete(save=False)  # Eliminar archivo
                    photo.delete()  # Eliminar registro
                except Photo.DoesNotExist:
                    pass

        # Eliminar videos seleccionados
        video_ids = request.POST.getlist('delete_videos')
        for video_id in video_ids:
            if video_id:  # Ignorar campos vacíos
                try:
                    video = Video.objects.get(id=video_id)
                    video.video_file.delete(save=False)  # Eliminar archivo
                    video.delete()  # Eliminar registro
                except Video.DoesNotExist:
                    pass

        # Actualizar fotos existentes
        for photo in vehicle.fotos.all():
            if f'change_photo_{photo.id}' in request.FILES:
                new_photo_file = request.FILES[f'change_photo_{photo.id}']
                photo.photo.delete(save=False)  # Eliminar el archivo físico antiguo
                photo.photo = new_photo_file  # Asignar el nuevo archivo
                photo.save()

        # Actualizar videos existentes
        for video in vehicle.videos.all():
            if f'change_video_{video.id}' in request.FILES:
                new_video_file = request.FILES[f'change_video_{video.id}']
                video.video_file.delete(save=False)  # Eliminar el archivo físico antiguo
                video.video_file = new_video_file  # Asignar el nuevo archivo
                video.save()

        # Guardar cambios en el vehículo
        vehicle.save()

        # Agregar nuevas fotos
        new_photos = request.FILES.getlist('fotos')
        for photo in new_photos:
            new_photo = Photo(photo=photo)
            new_photo.save()
            vehicle.fotos.add(new_photo)

        # Agregar nuevos videos
        new_videos = request.FILES.getlist('videos')
        for video in new_videos:
            new_video = Video(video_file=video)
            new_video.save()
            vehicle.videos.add(new_video)

        messages.success(request, 'Vehicle updated successfully!')
        return redirect('Car')

    # Para la petición GET
    car_makes = CarMake.objects.all()
    car_models = CarModel.objects.all()

    return render(request, 'gestioncar/edit_vehicle.html', {
        'vehicle': vehicle,
        'marcas': car_makes,
        'modelos': car_models,
        'title_conditions': TITLE_CHOICES,
        'vehicle_types': VEHICLE_TYPE_CHOICES,
        'transmission_types': TRANSMISSION_CHOICES,
    })



#-------------------CARRUSEL --------------------------------------------------


# Listar todos los slides del carrusel
@login_required
def carousel_list(request):
    carousels = Carousel.objects.filter(is_active=True).order_by('order')
    return render(request, 'gestioncar/carousel_list.html', {'carousels': carousels})

# Registrar un nuevo slide
@login_required
def register_carousel(request):
    if request.method == 'POST':
        title = request.POST.get('title').strip()
        description = request.POST.get('description').strip()
        image = request.FILES.get('image')
        link = request.POST.get('link', '').strip()
        show_title = 'show_title' in request.POST
        show_description = 'show_description' in request.POST
        show_slider = 'show_slider' in request.POST
        order = request.POST.get('order', 0)

        if not title or not image:
            messages.error(request, 'The title and image are required...')
        else:
            Carousel.objects.create(
                title=title,
                description=description,
                image=image,
                link=link,
                show_title=show_title,
                show_description=show_description,
                show_slider=show_slider,
                order=order
            )
            messages.success(request, 'Slide added successfully...')
            return redirect('carousel_list')

    return render(request, 'gestioncar/register_carousel.html')

# Eliminar un slide
@login_required
def delete_carousel(request, id):
    carousel = get_object_or_404(Carousel, id=id)
    # Eliminar el archivo físico
    if carousel.image:
        if os.path.isfile(carousel.image.path):
            os.remove(carousel.image.path)
    # Eliminar el registro de la base de datos
    carousel.delete()
    messages.success(request, 'Slide delete successfully...')
    return redirect('carousel_list')

# Editar un slide
@login_required
def edit_carousel(request, id):
    carousel = get_object_or_404(Carousel, id=id)

    if request.method == 'POST':
        # Guardar los nuevos valores
        carousel.title = request.POST.get('title').strip()
        carousel.description = request.POST.get('description').strip()
        carousel.link = request.POST.get('link', '').strip()
        carousel.show_title = 'show_title' in request.POST
        carousel.show_description = 'show_description' in request.POST
        carousel.show_slider = 'show_slider' in request.POST
        carousel.order = request.POST.get('order', 0)

        # Si se proporciona una nueva imagen, eliminar la anterior
        if 'image' in request.FILES:
            if carousel.image:  # Verificar si hay una imagen anterior
                if os.path.isfile(carousel.image.path):  # Verificar si el archivo existe
                    os.remove(carousel.image.path)  # Eliminar el archivo físico
            carousel.image = request.FILES['image']  # Asignar la nueva imagen

        carousel.save()
        messages.success(request, 'Slide update successfully.')
        return redirect('carousel_list')

    return render(request, 'gestioncar/edit_carousel.html', {'carousel': carousel})

# ----------------- CRUD VENDOR (Admin only) -----------------
@user_passes_test(is_admin)
def vendor_list(request):
    vendors = User.objects.filter(profile__role='Vendor').select_related('profile')
    return render(request, 'gestioncar/vendor_list.html', {'vendors': vendors})

@user_passes_test(is_admin)
def register_vendor(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('vendor_list')
        
        # Crea el usuario sin perfil
        user = User.objects.create_user(
            username=username, 
            password=password, 
            email=email
        )
        
        # Actualiza el perfil existente (creado por la señal)
        user.profile.role = 'Vendor'
        user.profile.save()  # <-- ¡Usa save() en lugar de crear nuevo perfil!
        
        messages.success(request, 'Vendor created successfully!')
        return redirect('vendor_list')
    
    return render(request, 'gestioncar/register_vendor.html')

@user_passes_test(is_admin)
def delete_vendor(request, id):
    vendor = get_object_or_404(User, pk=id)
    if vendor.profile.role == 'Vendor':
        vendor.delete()
        messages.success(request, 'Vendor deleted successfully!')
    return redirect('vendor_list')

# ----------------- CRUD CLIENT (Public) -----------------
#@def client_list(request):
#    if not request.user.is_authenticated:
#        return redirect('login')
#    
 #   clients = User.objects.filter(profile__role='Client')
#    return render(request, 'gestioncar/client_list.html', {'clients': clients})
from smtplib import SMTPException
from django.core.exceptions import ValidationError

def public_register(request):
    if request.method == 'GET':
        return render(request, 'gestioncar/register.html')
    
    try:
        # Procesar POST
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        # Validar email único
        if User.objects.filter(email=email).exists():
            reset_url = reverse('password_reset')
            error_msg = mark_safe(f'Email ya registrado. <a href="{reset_url}">¿Recuperar contraseña?</a>')
            messages.error(request, error_msg)
            return redirect('public_register')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_active=False
        )
        
        # Asignar rol y guardar
        user.profile.role = 'Client'
        user.profile.save()
        
        # Generar email de activación
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = request.build_absolute_uri(
            reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Enviar email
        send_mail(
            subject='Verifica tu cuenta en Maxibidder',
            message=render_to_string('gestioncar/email_verification.html', {
                'user': user,
                'activation_url': activation_url,
                'site_name': 'Maxibidder'
            }),
            from_email='noreply@maxibidder.com',
            recipient_list=[email],
            fail_silently=False
        )
        
        messages.success(request, '¡Registro exitoso! Revisa tu email para activar la cuenta.')
        return redirect('login')

    except SMTPException as e:
        user.delete()
        messages.error(request, f'Error al enviar el email de verificación: {str(e)}')
        return redirect('public_register')
        
    except Exception as e:
        if 'user' in locals(): user.delete()
        messages.error(request, f'Error inesperado: {str(e)}')
        return redirect('public_register')


@user_passes_test(is_admin)
def client_list(request):
    clients = User.objects.filter(profile__role='Client')
    return render(request, 'gestioncar/client_list.html', {'clients': clients})

@login_required
def register_client(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        # Verificar si el usuario actual es Admin para asignar rol
        if request.user.profile.role == 'Admin':
            role = request.POST.get('role', 'Client')
        else:
            role = 'Client'
        
        # Validar email existente
        if User.objects.filter(email=email).exists():
            reset_url = reverse('password_reset')
            error_msg = mark_safe(f'Email ya registrado. <a href="{reset_url}">¿Recuperar contraseña?</a>')
            messages.error(request, error_msg)
            return redirect('login')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username, 
            password=password, 
            email=email, 
            is_active=False
        )
        
        # Asignar rol desde el perfil
        #user.profile.role = role
        #user.profile.save()
        profile = user.profile  # Accede al perfil existente
        profile.role = role
        profile.save()  

        
        # Generar token de activación
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construir enlace de activación
        activation_url = reverse('activate_account', kwargs={
            'uidb64': uid,
            'token': token
        })
        full_activation_url = request.build_absolute_uri(activation_url)
        
        # Crear y enviar email
        subject = 'Verifica tu cuenta en Maxibidder'
        message = render_to_string('gestioncar/email_verification.html', {
            'user': user,
            'activation_url': full_activation_url,
            'site_name': 'Maxibidder'
        })
        
        send_mail(
            subject,
            message,
            'noreply@maxibidder.com',  # Email remitente
            [email],  # Email destinatario
            fail_silently=False,
        )
        
        messages.success(request, '¡Usuario creado! Revisa tu email para activar la cuenta.')
        return redirect('login')
    
    return redirect('login')
    
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated! You can now login.')
    else:
        messages.error(request, 'Invalid activation link.')
    
    return redirect('login')    

@login_required
def edit_client(request, id):
    client = get_object_or_404(User, pk=id)
    profile = client.profile
    
    if request.user != client and not request.user.profile.role == 'Admin':
        raise PermissionDenied

    if request.method == 'POST':
        # Actualizar perfil
        if 'update_profile' in request.POST:
            client.email = request.POST.get('email', client.email)
            profile.phone = request.POST.get('phone', profile.phone)
            client.first_name = request.POST.get('first_name', client.first_name)
            client.last_name = request.POST.get('last_name', client.last_name)
            profile.receive_newsletter = 'receive_newsletter' in request.POST
            profile.receive_notifications = 'receive_notifications' in request.POST
            profile.receive_catalog = 'receive_catalog' in request.POST
            client.save()
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_client', id=id)
        
        # Cambiar contraseña
        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not client.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match')
            else:
                client.set_password(new_password1)
                client.save()
                update_session_auth_hash(request, client)  # ¡Ahora está definido!
                messages.success(request, 'Password updated successfully!')
            
            return redirect('edit_client', id=id)

    return render(request, 'gestioncar/edit_client.html', {
        'client': client,
        'profile': profile
    })


class CustomLoginView(auth_views.LoginView):
    template_name = 'gestioncar/login.html'  # Asegúrate de que coincida con tu template

    def form_invalid(self, form):
        messages.error(self.request, '⚠️ Usuario o contraseña incorrectos.')
        return super().form_invalid(form)