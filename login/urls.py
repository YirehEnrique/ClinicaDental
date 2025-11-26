from django.urls import path
from login import views


urlpatterns = [
    path('', views.login_view, name='Inicio_login'), #ruta raiz de login
    path('logout/', views.logout_view, name='logout'), #ruta para salir
    path('register/', views.register_view, name='register'), #ruta para registrar usuario
]