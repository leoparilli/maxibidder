from django.contrib import admin

# Register your models here.
from gestioncar.models import CarMake, CarModel, Photo, Video, Vehicle, Carousel, Profile

admin.site.register(CarMake)
admin.site.register(CarModel)
admin.site.register(Photo)
admin.site.register(Video)
admin.site.register(Vehicle)
admin.site.register(Carousel)
admin.site.register(Profile)