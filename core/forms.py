# core/forms.py

from django import forms
from .models import Embarcacao, Viagem, InfoPassageiro

class EmbarcacaoForm(forms.ModelForm):
    class Meta:
        model = Embarcacao
        fields = ['nome', 'capacidade']

class ViagemForm(forms.ModelForm):
    class Meta:
        model = Viagem
        fields = ['embarcacao', 'origem', 'destino', 'data_partida', 'data_chegada', 'preco', 'vagas_disponiveis']
        widgets = {
            'data_partida': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_chegada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        # Pega o usuário que foi passado pela view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Se um usuário foi passado, filtra o queryset de embarcações
        if user:
            self.fields['embarcacao'].queryset = Embarcacao.objects.filter(proprietario=user)


class InfoPassageiroForm(forms.ModelForm):
    
    # 1. Definindo as opções para os campos de escolha
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
        ('Outro', 'Outro'),
    ]
    TIPO_DOCUMENTO_CHOICES = [
        ('CPF', 'CPF'),
        ('RG', 'RG'),
        ('Passaporte', 'Passaporte'),
    ]

    # 2. Transformando campos de texto em campos de seleção (dropdown)
    genero = forms.ChoiceField(choices=GENERO_CHOICES)
    tipo_documento = forms.ChoiceField(choices=TIPO_DOCUMENTO_CHOICES)
    
    class Meta:
        model = InfoPassageiro
        # 3. Excluindo o campo 'passagem', pois ele será associado automaticamente
        exclude = ['passagem']
        
        # 4. Personalizações (rótulos e placeholders)
        labels = {
            'nome_completo': 'Nome Completo*',
            'email': 'Email*',
            'data_nascimento': 'Data de Nascimento*',
            'contato': 'Contato*',
            'nacionalidade': 'Nacionalidade*',
            'cep': 'CEP*',
            'numero_documento': 'Número do Documento*',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa'}),
            'contato': forms.TextInput(attrs={'placeholder': '(xx) xxxxx-xxxx'}),
            'cep': forms.TextInput(attrs={'placeholder': 'xxxxx-xxx'}),
            'numero_documento': forms.TextInput(attrs={'placeholder': 'xxx.xxx.xxx-xx'}),
        }