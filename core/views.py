from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Viagem, Passagem, Embarcacao
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .forms import EmbarcacaoForm, ViagemForm, InfoPassageiroForm

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
    
    # 1. Pega o novo parâmetro de ordenação da URL
    sort_by = request.GET.get('sort')

    resultados = Viagem.objects.all()

    # Filtros (como antes)
    if origem:
        resultados = resultados.filter(origem__icontains=origem)
    if destino:
        resultados = resultados.filter(destino__icontains=destino)
    if data_ida:
        resultados = resultados.filter(data_partida__date=data_ida)

    # 2. NOVA LÓGICA DE ORDENAÇÃO
    if sort_by == 'menor_preco':
        resultados = resultados.order_by('preco') # Ordena do menor para o maior
    elif sort_by == 'maior_preco':
        resultados = resultados.order_by('-preco') # O '-' inverte a ordem (maior para o menor)
    else:
        # Ordem padrão se nenhum filtro for aplicado
        resultados = resultados.order_by('data_partida')

    context = {
        'resultados': resultados,
        'origem_busca': origem,
        'destino_busca': destino,
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

@login_required
def comprar_passagem(request, viagem_id):
    # Apenas aceitamos requisições do tipo POST para esta ação
    if request.method == 'POST':
        viagem = get_object_or_404(Viagem, pk=viagem_id)
        passageiro = request.user

        # VERIFICAÇÃO 1: O usuário já comprou uma passagem para esta viagem?
        if Passagem.objects.filter(passageiro=passageiro, viagem=viagem).exists():
            messages.warning(request, 'Você já possui uma passagem para esta viagem.')
            return redirect('detalhes_viagem', viagem_id=viagem.id)

        # VERIFICAÇÃO 2: Ainda existem vagas disponíveis?
        if viagem.vagas_disponiveis > 0:
            # Se houver vagas, cria a passagem no banco de dados
            Passagem.objects.create(passageiro=passageiro, viagem=viagem)
            
            # Decrementa (diminui em 1) o número de vagas
            viagem.vagas_disponiveis -= 1
            viagem.save()
            
            messages.success(request, 'Sua passagem foi comprada com sucesso!')
            # No futuro, podemos redirecionar para a página "Minhas Passagens"
            return redirect('home')
        else:
            # Se não houver vagas, informa o usuário
            messages.error(request, 'Não há mais vagas disponíveis para esta viagem.')
            return redirect('detalhes_viagem', viagem_id=viagem.id)
    
    # Se alguém tentar acessar esta URL via GET, apenas redireciona para a home
    return redirect('home')

@login_required
def minhas_passagens(request):
    # 1. Filtra o banco de dados para pegar apenas as passagens
    #    do usuário que está logado no momento (request.user).
    # 2. O '-data_compra' ordena o resultado da mais recente para a mais antiga.
    passagens = Passagem.objects.filter(passageiro=request.user).order_by('-data_compra')

    context = {
        'passagens': passagens
    }

    return render(request, 'minhas_passagens.html', context)

@login_required
def dashboard(request):
    if not request.user.groups.filter(name='Donos de Barco').exists():
        messages.error(request, 'Acesso negado. Esta página é apenas para donos de embarcações.')
        return redirect('home')
    
    minhas_embarcacoes = Embarcacao.objects.filter(proprietario=request.user)
    
    minhas_viagens = Viagem.objects.filter(embarcacao__proprietario=request.user).order_by('data_partida')
    
    context = {
        'embarcacoes': minhas_embarcacoes,
        'viagens': minhas_viagens, # Adiciona as viagens ao contexto
    }
    # --- FIM DA ALTERAÇÃO ---
    
    return render(request, 'dashboard.html', context)

@login_required
def adicionar_embarcacao(request):
    # Garante que apenas donos de barco acessem esta página
    if not request.user.groups.filter(name='Donos de Barco').exists():
        messages.error(request, 'Acesso negado.')
        return redirect('home')

    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        form = EmbarcacaoForm(request.POST)
        if form.is_valid():
            # 1. Cria o objeto embarcação, mas não salva no banco ainda
            embarcacao = form.save(commit=False)
            # 2. Associa o proprietário como sendo o usuário logado
            embarcacao.proprietario = request.user
            # 3. Agora sim, salva o objeto completo no banco
            embarcacao.save()
            
            messages.success(request, 'Embarcação adicionada com sucesso!')
            return redirect('dashboard') # Redireciona para o dashboard
    # Se a página foi apenas acessada (método GET)
    else:
        form = EmbarcacaoForm() # Cria um formulário em branco

    context = {'form': form}
    return render(request, 'adicionar_embarcacao.html', context)

@login_required
def editar_embarcacao(request, embarcacao_id):
    # Busca a embarcação específica pelo ID
    embarcacao = get_object_or_404(Embarcacao, pk=embarcacao_id)
    
    # VERIFICAÇÃO DE SEGURANÇA: Garante que o usuário logado é o dono do barco
    if embarcacao.proprietario != request.user:
        messages.error(request, 'Acesso negado. Você não é o proprietário desta embarcação.')
        return redirect('dashboard')

    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        # Cria o formulário com os dados enviados E com a instância do barco a ser atualizado
        form = EmbarcacaoForm(request.POST, instance=embarcacao)
        if form.is_valid():
            form.save() # Salva as alterações no objeto existente
            messages.success(request, 'Embarcação atualizada com sucesso!')
            return redirect('dashboard')
    # Se a página foi apenas acessada (método GET)
    else:
        # Cria o formulário preenchido com os dados da embarcação existente
        form = EmbarcacaoForm(instance=embarcacao)

    context = {'form': form}
    return render(request, 'editar_embarcacao.html', context)

@login_required
def apagar_embarcacao(request, embarcacao_id):
    # Busca a embarcação e faz a checagem de segurança (se o usuário é o dono)
    embarcacao = get_object_or_404(Embarcacao, pk=embarcacao_id)
    if embarcacao.proprietario != request.user:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    # Se o formulário de confirmação foi enviado
    if request.method == 'POST':
        embarcacao.delete() # O comando para apagar o objeto do banco
        messages.success(request, f'A embarcação "{embarcacao.nome}" foi apagada com sucesso.')
        return redirect('dashboard')
    
    # Se a página foi apenas acessada (GET), mostra a tela de confirmação
    context = {'embarcacao': embarcacao}
    return render(request, 'apagar_confirm.html', context)

@login_required
def adicionar_viagem(request):
    # Garante que apenas donos de barco acessem esta página
    if not request.user.groups.filter(name='Donos de Barco').exists():
        messages.error(request, 'Acesso negado.')
        return redirect('home')

    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        # Passa os dados do POST e o usuário para o formulário
        form = ViagemForm(request.POST, user=request.user)
        if form.is_valid():
            form.save() # O ModelForm já sabe como criar a Viagem
            messages.success(request, 'Nova viagem programada com sucesso!')
            return redirect('dashboard')
    # Se a página foi apenas acessada (método GET)
    else:
        # Passa o usuário para o formulário para filtrar as embarcações
        form = ViagemForm(user=request.user)

    context = {'form': form}
    return render(request, 'adicionar_viagem.html', context)

@login_required
def editar_viagem(request, viagem_id):
    # Busca a viagem específica pelo ID
    viagem = get_object_or_404(Viagem, pk=viagem_id)
    
    # VERIFICAÇÃO DE SEGURANÇA: Garante que o usuário logado é o dono da embarcação desta viagem
    if viagem.embarcacao.proprietario != request.user:
        messages.error(request, 'Acesso negado. Você não tem permissão para editar esta viagem.')
        return redirect('dashboard')

    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        # Cria o formulário com os dados enviados e com a instância da viagem a ser atualizada
        form = ViagemForm(request.POST, instance=viagem, user=request.user)
        if form.is_valid():
            form.save() # Salva as alterações
            messages.success(request, 'Viagem atualizada com sucesso!')
            return redirect('dashboard')
    # Se a página foi apenas acessada (método GET)
    else:
        # Cria o formulário preenchido com os dados da viagem existente
        form = ViagemForm(instance=viagem, user=request.user)

    context = {
        'form': form,
        'viagem': viagem # Enviamos a viagem para usar o nome no título, por exemplo
    }
    return render(request, 'editar_viagem.html', context)

@login_required
def apagar_viagem(request, viagem_id):
    # Busca a viagem e faz a checagem de segurança (se o usuário é o dono)
    viagem = get_object_or_404(Viagem, pk=viagem_id)
    if viagem.embarcacao.proprietario != request.user:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    # Se o formulário de confirmação foi enviado (método POST)
    if request.method == 'POST':
        nome_viagem = f"Viagem de {viagem.origem} para {viagem.destino}"
        viagem.delete() # O comando para apagar o objeto do banco
        messages.success(request, f'A viagem "{nome_viagem}" foi apagada com sucesso.')
        return redirect('dashboard')
    
    # Se a página foi apenas acessada (GET), mostra a tela de confirmação
    context = {'viagem': viagem}
    return render(request, 'apagar_viagem_confirm.html', context)

@login_required
def checkout_view(request, viagem_id):
    viagem = get_object_or_404(Viagem, pk=viagem_id)
    
    # Se o formulário foi enviado (método POST)
    if request.method == 'POST':
        form = InfoPassageiroForm(request.POST)
        if form.is_valid():
            # PASSO 1: Criar o objeto Passagem (a "compra")
            # Por enquanto, não diminuímos as vagas. Faremos isso após o pagamento.
            nova_passagem = Passagem.objects.create(
                passageiro=request.user,
                viagem=viagem
            )
            
            # PASSO 2: Criar o objeto InfoPassageiro e associá-lo à passagem
            info_passageiro = form.save(commit=False)
            info_passageiro.passagem = nova_passagem
            info_passageiro.save()
            
            # PASSO 3: Redirecionar para a página de pagamento
            # Passamos o ID da nova passagem para a próxima etapa
            return redirect('pagamento', passagem_id=nova_passagem.id)
            
    # Se a página foi apenas acessada (método GET)
    else:
        form = InfoPassageiroForm()

    context = {
        'form': form,
        'viagem': viagem,
    }
    return render(request, 'checkout.html', context)

@login_required
def pagamento_view(request, passagem_id):
    passagem = get_object_or_404(Passagem, pk=passagem_id, passageiro=request.user)
    
    # Se o formulário de confirmação foi enviado (método POST)
    if request.method == 'POST':
        viagem = passagem.viagem
        
        # Lógica principal: Diminuir a vaga
        if viagem.vagas_disponiveis > 0:
            viagem.vagas_disponiveis -= 1
            viagem.save()
            
            # Aqui poderíamos mudar o status da passagem se tivéssemos um status "PENDENTE"
            # passagem.status = 'CONFIRMADO'
            # passagem.save()
            
            messages.success(request, 'Pagamento confirmado! Sua passagem foi gerada.')
            # Redireciona para a etapa final de confirmação
            return redirect('confirmacao_bilhete', passagem_id=passagem.id)
        else:
            messages.error(request, 'Desculpe, as vagas para esta viagem acabaram enquanto você concluía a compra.')
            return redirect('home')

    # Se a página foi apenas acessada (método GET)
    context = {'passagem': passagem}
    return render(request, 'pagamento.html', context)

@login_required
def confirmacao_view(request, passagem_id):
    passagem = get_object_or_404(Passagem, pk=passagem_id, passageiro=request.user)
    context = {'passagem': passagem}
    return render(request, 'confirmacao_bilhete.html', context)