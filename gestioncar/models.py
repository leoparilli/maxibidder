import os
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.

TRANSMISSION_CHOICES = [
    ('Manual', 'Manual'),
    ('Automatic', 'Automatic'),
    ('CVT', 'Continuously Variable Transmission (CVT)'),
    ('DSG/DGT', 'Dual Clutch (DSG or DGT)'),
    ('AMT', 'Manual Automated (AMT)'),
    ('Sequential Manual', 'Manual Sequential'),
    ('EVT', 'Electronic Variable Transmission (EVT)'),
    ('Hydraulic', 'Hydraulic'),
]    


VEHICLE_TYPE_CHOICES = [
    ('Sedan', 'Sedan'),
    ('SUV', 'SUV'),
    ('Truck', 'Truck'),
    ('Van', 'Van'),
    ('Coupe', 'Coupe'),
    ('Wagon', 'Wagon'),
    ('Hatchback', 'Hatchback'),
]
 

TITLE_CHOICES = [
    ('Clean', 'Clean'),
    ('Rebuilt', 'Rebuilt'),
    ('Salvage', 'Salvage'),
]

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Vendor', 'Vendor'),
        ('Client', 'Client'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=13, choices=ROLE_CHOICES, default='Client')
    created_at = models.DateTimeField(auto_now_add=True)
    # Nuevos campos adicionales
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    receive_newsletter = models.BooleanField(default=True, verbose_name="Receive newsletter")
    receive_notifications = models.BooleanField(default=True, verbose_name="Receive notifications")
    receive_catalog = models.BooleanField(default=True, verbose_name="Receive monthly catalog")

    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class CarMake(models.Model):
    make = models.CharField(max_length=30, unique=True, verbose_name="CarMake")
    def __str__(self):
        return self.make
 
    
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    model_make = models.CharField(max_length=50)

    class Meta:
        unique_together = ('make', 'model_make')
    
    def __str__(self):
        return f"{self.make.make} - {self.model_make}"
    

class Photo(models.Model):
    photo = models.ImageField(upload_to='img_car_vid/ima_car/')
    def __str__(self):
        return self.photo.name 
class Video(models.Model):
    video_file = models.FileField(upload_to='img_car_vid/ima_vid/')
    def __str__(self):
        return self.video_file.name

class Vehicle(models.Model):
    stock = models.CharField(max_length=7, unique=True)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='cars_make')
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars_model')
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    mileage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
  
    #title_condition = models.CharField(max_length=10, choices=TITLE_CHOICES, verbose_name="Title Condition")
    title_condition = models.CharField(max_length=10, choices=TITLE_CHOICES, verbose_name="Title Condition", null=True)
    transmission = models.CharField(max_length=30, choices=TRANSMISSION_CHOICES, verbose_name="transmission")
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPE_CHOICES, verbose_name="vehicle_type")

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Only USD") 
    details = models.TextField(blank=True, null=True, help_text='Enter additional details about the vehicle')  

    foto_principal = models.ImageField(upload_to='img_car_vid/ima_car/', null=True)    
    fotos = models.ManyToManyField(Photo, related_name='photos_car', blank=True)
    videos = models.ManyToManyField(Video, related_name='videos_carro', blank=True)    
    links = models.TextField(blank=True, null=True, help_text='Enter one or more URLs, separated by line breaks')    
    #date_add = models.DateField(default=None, null=True) 
    date_add = models.DateField(auto_now_add=True)  # Solo auto_now_add

    def __str__(self):
        return f"{self.stock}"
    
#

#C----------CARRUSEL -------------------------------
class Carousel(models.Model):
    title = models.CharField(max_length=100, verbose_name="Title")
    description = models.TextField(blank=True, null=True, verbose_name="Descriptions")
    image = models.ImageField(upload_to='ima_carousel/', verbose_name="Image")
    link = models.URLField(blank=True, null=True, verbose_name="Link")  # Nuevo campo para el enlace
    show_title = models.BooleanField(default=True, verbose_name="Show Title")  # Checkbox para mostrar título
    show_description = models.BooleanField(default=True, verbose_name="Show Description")  # Checkbox para mostrar descripción
    show_slider = models.BooleanField(default=True, verbose_name="Show Slider")  # Checkbox para mostrar el slider
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico antes de eliminar el registro
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)  # Llamar al método delete original

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    #if created:
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()

@receiver(post_save, sender=User)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea perfil SOLO para nuevos usuarios"""
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Actualiza el perfil existente"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

