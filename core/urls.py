# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('viagem/<int:viagem_id>/', views.detalhes_viagem, name='detalhes_viagem'),
    path('buscar/', views.buscar, name='buscar'),
    path('registrar/', views.registrar, name='registrar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]