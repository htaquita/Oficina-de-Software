from django.shortcuts import render, get_object_or_404, redirect
from .models import Viagem
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 1. Salva o formulário E pega o novo objeto de usuário criado
            user = form.save() 
            username = form.cleaned_data.get('username')
            
            # 2. Faz o login do novo usuário na sessão atual
            login(request, user)
            
            # 3. A mensagem agora é de boas-vindas, não de "faça o login"
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}!')
            
            return redirect('home')
    else:
        form = UserCreationForm()
        
    context = {'form': form}
    return render(request, 'registrar.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Pega os dados limpos do formulário
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autentica o usuário
            user = authenticate(username=username, password=password)
            
            # Se o usuário for válido, inicia a sessão
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo de volta, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
        
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta com sucesso.')
    return redirect('home')