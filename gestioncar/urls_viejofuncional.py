from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

from . import views


def is_admin(user):
    return user.is_authenticated and user.profile.role == 'Admin'

urlpatterns = [
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # Redirige a la página principal después de cerrar sesión

    path('', views.home, name= "Home"),

    path('inventory', views.inventory, name= "Inventory"),
    path('inventory/<int:pk>/', views.vehicle_detail, name='car_detail'),




    path('car_finder', views.car_finder, name= "Car_Finder"),
    path('buy_with_us', views.buy_with_us, name= "Buy_With_Us"),
    path('about_us', views.about_us, name= "About_Us"),
    path('my_account', views.my_account, name= "My_Account"),
    path('admin_maxibidder', views.admin_maxibidder, name= "Admin_Maxibidder"),

    path('contact_us', views.contact_us, name="contact_us"),
    
    path('login/', auth_views.LoginView.as_view(template_name='gestioncar/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='Home'), name='logout'), 
    
# URLs protegidas para Admin (Make)
    path('admin_maxibidder/make', views.make, name="Make"),  #listar brand
    path('register_brand/',  views.register_brand, name="register_brand"), #Agrega brand guardar
    path('delete_brand/<int:id>', views.delete_brand, name="delete_brand"), #Eliminar Brand
    path('brand_detail/<int:id>', views.brand_detail, name="brand_detail"), #Modificar o editar brand
    path('brandedit/',  views.brandedit, name="brandedit"),#para el formulario editar-update
    

    path('admin_maxibidder/model', views.a_model, name="Model"),  #listar Model
    path('register_model/', views.register_model, name="register_model"), #guardar o registrar
    path('delete_model/<int:id>', views.delete_model, name="delete_model"), #eliminar
    path('model_detail/<int:id>', views.model_detail, name="model_detail"), #detalle para modificar
    path('modeledit/', views.modeledit, name="modeledit"), #para editar



    path('car/', views.car, name="Car"),
    path('get_models/<int:make_id>/', views.get_models, name='get_models'),  #Carga y filtra los modelos de acuerdo a la marca
    path('delete_vehicle/<int:id>', views.delete_vehicle, name='delete_vehicle'),
    path('edit_vehicle/<int:id>', views.edit_vehicle, name='edit_vehicle'),


    path('admin_maxibidder/carousel', views.carousel_list, name="carousel_list"),
    path('register_carousel/', views.register_carousel, name="register_carousel"),
    path('delete_carousel/<int:id>', views.delete_carousel, name="delete_carousel"),
    path('edit_carousel/<int:id>', views.edit_carousel, name="edit_carousel"),
   
]


# Servir archivos multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)