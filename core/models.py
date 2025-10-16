# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Embarcacao(models.Model):
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE) # <-- MUDANÇA IMPORTANTE
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField()
    tipo = models.CharField(max_length=50, default='Outro')

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
    
class Passagem(models.Model):
    passageiro = models.ForeignKey(User, on_delete=models.CASCADE)
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE)
    data_compra = models.DateTimeField(auto_now_add=True)
    
    # Podemos adicionar um status para o futuro, é uma boa prática
    STATUS_CHOICES = [
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMADO')

    def __str__(self):
        return f"Passagem de {self.passageiro.username} para {self.viagem.destino}"
    

class InfoPassageiro(models.Model):
    # Cria uma ligação estrita: cada passagem tem UMA info de passageiro
    passagem = models.OneToOneField(Passagem, on_delete=models.CASCADE)
    
    nome_completo = models.CharField(max_length=200)
    email = models.EmailField()
    genero = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    contato = models.CharField(max_length=20)
    nacionalidade = models.CharField(max_length=50)
    cep = models.CharField(max_length=10)
    tipo_documento = models.CharField(max_length=20)
    numero_documento = models.CharField(max_length=50, unique=True) # CPF/RG deve ser único

    def __str__(self):
        return self.nome_completo