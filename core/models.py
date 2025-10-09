# core/models.py
from django.db import models

class Embarcacao(models.Model):
    nome = models.CharField(max_length=100)
    dono = models.CharField(max_length=100)
    capacidade = models.IntegerField()

    def __str__(self):
        return self.nome

class Viagem(models.Model):
    # A ForeignKey cria a relação: uma Viagem pertence a uma Embarcacao.
    embarcacao = models.ForeignKey(Embarcacao, on_delete=models.CASCADE)
    origem = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    data_partida = models.DateTimeField()
    data_chegada = models.DateTimeField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    vagas_disponiveis = models.IntegerField()

    def __str__(self):
        return f"{self.origem} -> {self.destino} ({self.embarcacao.nome})"