"""
URL configuration for maxibidder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views  #nuevo en la noche 12

#importar las URLs
# from gestioncar import views   NO LO NECESITO PORQUE YA TENGO LAS URL EN LA APLICACION

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('gestioncar/', include('gestioncar.urls')),  # Corrige aquí si es necesario
    path('accounts/', include('django.contrib.auth.urls')), #nuevo en la noche 12

    path('', include('gestioncar.urls')), #corrige que no tenga que incluir en url la direccion de la aplicacion
    
]
