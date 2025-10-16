# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('viagem/<int:viagem_id>/', views.detalhes_viagem, name='detalhes_viagem'),
    path('viagem/<int:viagem_id>/comprar/', views.comprar_passagem, name='comprar_passagem'),
    path('viagem/<int:viagem_id>/checkout/', views.checkout_view, name='checkout'),
    path('passagem/<int:passagem_id>/pagamento/', views.pagamento_view, name='pagamento'),
    path('buscar/', views.buscar, name='buscar'),
    path('registrar/', views.registrar, name='registrar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('minhas-passagens/', views.minhas_passagens, name='minhas_passagens'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/adicionar-barco/', views.adicionar_embarcacao, name='adicionar_embarcacao'),
    path('dashboard/editar-barco/<int:embarcacao_id>/', views.editar_embarcacao, name='editar_embarcacao'),
    path('dashboard/apagar-barco/<int:embarcacao_id>/', views.apagar_embarcacao, name='apagar_embarcacao'),
    path('dashboard/adicionar-viagem/', views.adicionar_viagem, name='adicionar_viagem'),
    path('dashboard/editar-viagem/<int:viagem_id>/', views.editar_viagem, name='editar_viagem'),
    path('dashboard/apagar-viagem/<int:viagem_id>/', views.apagar_viagem, name='apagar_viagem'),
    path('passagem/<int:passagem_id>/confirmacao/', views.confirmacao_view, name='confirmacao_bilhete'),
]