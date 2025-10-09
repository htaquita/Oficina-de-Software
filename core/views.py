from django.shortcuts import render, get_object_or_404, redirect
from .models import Viagem
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def home(request):
    viagens_saindo_manaus = Viagem.objects.filter(origem="Manaus")
    viagens_para_manaus = Viagem.objects.filter(destino="Manaus")
    
    origens_unicas = Viagem.objects.order_by('origem').values_list('origem', flat=True).distinct()
    
    destinos_unicos = Viagem.objects.order_by('destino').values_list('destino', flat=True).distinct()
    
    lista_cidades = sorted(list(set(list(origens_unicas) + list(destinos_unicos))))

    context = {
        'viagens_saindo': viagens_saindo_manaus,
        'viagens_chegando': viagens_para_manaus,
        'cidades': lista_cidades, # 4. Envia a lista de cidades para o template
    }
    return render(request, 'index.html', context)


def detalhes_viagem(request, viagem_id):
    viagem = get_object_or_404(Viagem, pk=viagem_id)
    
    context = {
        'viagem': viagem
    }
    return render(request, 'detalhes_viagem.html', context)

def buscar(request):
    origem = request.GET.get('origem')
    destino = request.GET.get('destino')
    data_ida = request.GET.get('data_ida')

    resultados = Viagem.objects.all()

    if origem:
        resultados = resultados.filter(origem__icontains=origem)

    if destino:
        resultados = resultados.filter(destino__icontains=destino)

    if data_ida:
        resultados = resultados.filter(data_partida__date=data_ida)

    context = {
        'resultados': resultados
    }

    return render(request, 'resultados_busca.html', context)

def registrar(request):
    # Se o método for POST, significa que o usuário enviou o formulário
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # Se o formulário for válido...
        if form.is_valid():
            form.save() # Salva o novo usuário no banco de dados
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Você já pode fazer o login.')
            return redirect('home') # Redireciona para a página inicial
    # Se for um GET, apenas mostra um formulário em branco
    else:
        form = UserCreationForm()
        
    context = {'form': form}
    return render(request, 'registrar.html', context)