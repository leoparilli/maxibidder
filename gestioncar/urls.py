from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

from . import views
from .views import is_admin
from .views import CustomLoginView  # Importa la vista personalizada


def is_admin(user):
    return user.is_authenticated and user.profile.role == 'Admin'

urlpatterns = [
    
    path('', views.home, name="Home"),
    path('inventory', views.inventory, name="Inventory"),
    path('inventory/<int:pk>/', views.vehicle_detail, name='car_detail'),
    path('car_finder', views.car_finder, name="Car_Finder"),
    path('buy_with_us', views.buy_with_us, name="Buy_With_Us"),
    path('about_us', views.about_us, name="About_Us"),
    path('contact_us', views.contact_us, name="contact_us"),
    path('compare/', views.compare, name='compare'),

    

    # URLs de autenticación (sin duplicados)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    path('login/', CustomLoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='Home'), name='logout'),
    path('403/', views.handler403, name='handler403'),

    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),



    # URLs protegidas para Admin (Make)
    path('admin_maxibidder/make', user_passes_test(is_admin)(views.make), name="Make"),
    path('register_brand/', user_passes_test(is_admin)(views.register_brand), name="register_brand"),
    path('delete_brand/<int:id>', user_passes_test(is_admin)(views.delete_brand), name="delete_brand"),
    path('brand_detail/<int:id>', user_passes_test(is_admin)(views.brand_detail), name="brand_detail"),
    path('brandedit/', user_passes_test(is_admin)(views.brandedit), name="brandedit"),

    # URLs protegidas para Admin (Model)
    path('admin_maxibidder/model', user_passes_test(is_admin)(views.a_model), name="Model"),
    path('register_model/', user_passes_test(is_admin)(views.register_model), name="register_model"),
    path('delete_model/<int:id>', user_passes_test(is_admin)(views.delete_model), name="delete_model"),
    path('model_detail/<int:id>', user_passes_test(is_admin)(views.model_detail), name="model_detail"),
    path('modeledit/', user_passes_test(is_admin)(views.modeledit), name="modeledit"),

    # URLs protegidas para Admin (Carousel)
    path('admin_maxibidder/carousel', user_passes_test(is_admin)(views.carousel_list), name="carousel_list"),
    path('register_carousel/', user_passes_test(is_admin)(views.register_carousel), name="register_carousel"),
    path('delete_carousel/<int:id>', user_passes_test(is_admin)(views.delete_carousel), name="delete_carousel"),
    path('edit_carousel/<int:id>', user_passes_test(is_admin)(views.edit_carousel), name="edit_carousel"),

    # URLs accesibles para Vendor y Admin (Car)
    path('car/', views.car, name="Car"),
    path('get_models/<int:make_id>/', views.get_models, name='get_models'),
    path('delete_vehicle/<int:id>', views.delete_vehicle, name='delete_vehicle'),
    path('edit_vehicle/<int:id>', views.edit_vehicle, name='edit_vehicle'),

    # Otras URLs
    path('my_account', views.my_account, name="My_Account"),
    path('admin_maxibidder', views.admin_maxibidder, name="admin_maxibidder"),


    # Vendor CRUD
    path('admin_maxibidder/vendors', user_passes_test(is_admin)(views.vendor_list), name="vendor_list"),
    path('register_vendor/', user_passes_test(is_admin)(views.register_vendor), name="register_vendor"),
    path('delete_vendor/<int:id>', user_passes_test(is_admin)(views.delete_vendor), name="delete_vendor"),

    # Client CRUD
    path('clients/', views.client_list, name="client_list"),
    #path('register/client/', views.register_client, name="register_client"),
    path('register/client/', user_passes_test(is_admin)(views.register_client), name='register_client'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('edit_client/<int:id>', views.edit_client, name="edit_client"),


    #otra puebra de registro 19-02-2024
    path('register/', views.public_register, name='public_register'),
    path('admin/register/', user_passes_test(is_admin)(views.register_client), name='register_client'),

    # Password reset (incorporado de Django)
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='gestioncar/password_reset.html'), name='password_reset'),
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='gestioncar/password_reset.html', email_template_name='gestioncar/password_reset_email.html', subject_template_name='gestioncar/password_reset_subject.txt' ), name='password_reset'),

    #path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='gestioncar/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view( template_name='gestioncar/password_reset_done.html'), name='password_reset_done'),
    
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='gestioncar/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='gestioncar/password_reset_confirm.html'),name='password_reset_confirm'),

    #path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='gestioncar/password_reset_complete.html'), name='password_reset_complete'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='gestioncar/password_reset_complete.html'),name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)