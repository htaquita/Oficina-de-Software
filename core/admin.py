# core/admin.py

from django.contrib import admin
from .models import Embarcacao, Viagem, Passagem, InfoPassageiro

# Registre seus modelos aqui para que apareçam no painel de admin
admin.site.register(Embarcacao)
admin.site.register(Viagem)
admin.site.register(Passagem)
admin.site.register(InfoPassageiro)