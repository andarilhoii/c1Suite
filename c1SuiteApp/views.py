from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .models import Perfil, Permissao, Usuario
from .forms import LoginForm, UsuarioForm
from django.urls import reverse       
from django.contrib import messages   

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = LoginForm()
    # Corrigido aqui o caminho do template
    return render(request, 'c1SuiteApp/pages/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def perfis_view(request):
    #CREATE/UPDATE
    if request.method == 'POST' and request.POST.get('acao') == 'salvar':
        perfil_id = request.POST.get('id')
        nome = request.POST.get('nome') 
        descricao = request.POST.get('descricao', '')

        if perfil_id: #atualização
            perfil = get_object_or_404(Perfil, id=perfil_id)
            perfil.nome = nome
            perfil.descricao = descricao
            perfil.save()
        else: # inclusão
            Perfil.objects.create(nome=nome, descricao=descricao)
        return redirect('perfis')
    
    #DELETE
    if request. method == 'POST' and request.POST.get('acao') == 'excluir':
        perfil_id = request.POST.get('id')
        perfil = get_object_or_404(Perfil, id=perfil_id)
        perfil.delete()
        return redirect('perfis')
    
    #EDIT (carregar dados form)
    perfil_editar = None
    perfil_id = request.GET.get('editar')
    if perfil_id:
        perfil_editar = get_object_or_404(Perfil, id=perfil_id)
    perfis = Perfil.objects.all().order_by('nome')
    return render (
        request, 'c1SuiteApp/pages/perfis.html', {
            'perfis': perfis,
            'perfil_editar': perfil_editar
        },
    )
    
    # LIMPAR: só redireciona para a página sem parâmetros
    if request.method == 'POST' and request.POST.get('acao') == 'limpar':
        return redirect('perfis')
    
def permissoes_view(request):
    # CREATE / UPDATE
    if request.method == 'POST' and request.POST.get('acao') == 'salvar':
        permissoes_id = request.POST.get('id')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao', '')

        if permissoes_id:  # atualização
            permissao = get_object_or_404(Permissao, id=permissoes_id)
            permissao.nome = nome
            permissao.descricao = descricao
            permissao.save()
        else:  # inclusão
            Permissao.objects.create(nome=nome, descricao=descricao)

        return redirect('permissoes')

    # DELETE
    if request.method == 'POST' and request.POST.get('acao') == 'excluir':
        permissoes_id = request.POST.get('id')
        permissao = get_object_or_404(Permissao, id=permissoes_id)
        permissao.delete()
        return redirect('permissoes')

    # EDIT (carregar dados no form) - vem por GET: ?editar=ID
    permissao_editar = None
    permissoes_id = request.GET.get('editar')
    if permissoes_id:
        permissao_editar = get_object_or_404(Permissao, id=permissoes_id)

    permissoes = Permissao.objects.all().order_by('nome')
    return render(
        request,
        'c1SuiteApp/pages/permissoes.html',
        {
            'permissoes': permissoes,
            'permissoes_editar': permissao_editar,
        },
    )

def usuarios_view(request):
    usuarios = Usuario.objects.all()
    perfis = Perfil.objects.all().order_by("nome")

    editar_id = request.GET.get("editar")

    # ---------- MODO EDIÇÃO / NOVO ----------
    if editar_id:
        usuario_editar = get_object_or_404(Usuario, pk=editar_id)
        username_inicial = usuario_editar.username
        email_inicial = usuario_editar.email
        perfil_associado = getattr(usuario_editar, "perfil", None)
    else:
        usuario_editar = None
        username_inicial = ""
        email_inicial = ""
        perfil_associado = None

    # ---------- TRATAMENTO DO POST ----------
    if request.method == "POST":
        acao = request.POST.get("acao")

        # --- EXCLUSÃO vinda da lista ---
        if acao == "excluir":
            usuario_id = request.POST.get("usuario_id")

            if not usuario_id:
                messages.error(request, "ID de usuário inválido para exclusão.")
                return redirect(reverse("usuarios"))

            try:
                usuario_del = get_object_or_404(Usuario, pk=int(usuario_id))
            except (ValueError, TypeError):
                messages.error(request, "ID de usuário inválido para exclusão.")
                return redirect(reverse("usuarios"))

            usuario_del.delete()
            messages.success(request, "Usuário excluído com sucesso.")
            return redirect(reverse("usuarios"))

        # --- CADASTRO / EDIÇÃO ---
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "")
        perfil_id = request.POST.get("perfil_associado")
        ativo = request.POST.get("ativo") == "on"

        if not username or not email or not senha:
            messages.error(request, "Preencha usuário, e-mail e senha.")
        elif not perfil_id:
            messages.error(request, "Selecione um perfil para o usuário.")
        else:
            if usuario_editar:
                usuario = usuario_editar
            else:
                usuario = Usuario()

            usuario.username = username
            usuario.email = email
            usuario.set_password(senha)
            usuario.ativo = ativo
            usuario.perfil_id = perfil_id  # FK única
            usuario.save()

            messages.success(request, "Usuário salvo com sucesso.")
            return redirect(reverse("usuarios"))

    # ---------- RENDERIZAÇÃO ----------
    return render(
        request,
        "c1SuiteApp/pages/usuarios.html",
        {
            "usuarios": usuarios,
            "perfis": perfis,
            "usuario_editar": usuario_editar,
            "username_inicial": username_inicial,
            "email_inicial": email_inicial,
            "perfil_associado": perfil_associado,
        },
    )

def principal_view(request):
    return render(request, 'c1SuiteApp/pages/principal.html')
    
def perfis_permissoes_view(request):
    perfis = Perfil.objects.all().order_by('nome')
    permissoes = Permissao.objects.all().order_by('nome')

    if not perfis:
        return render(request, 'c1SuiteApp/pages/perfis_permissoes.html', {
            'perfis': [],
            'permissoes': permissoes,
            'perfil_selecionado': None,
            'permissoes_do_perfil': [],
        })

    # --- SALVAR (POST) ---
    if request.method == "POST":
        perfil_id = request.POST.get('perfil_id')
        permissoes_ids = request.POST.getlist('permissoes')  # lista de strings
        perfil = get_object_or_404(Perfil, id=perfil_id)
        # sobrescreve vínculos do perfil com o que veio marcado
        perfil.permissoes.set(permissoes_ids)
        # redireciona para GET do mesmo perfil
        return redirect(f'/perfis-permissoes/?perfil={perfil.id}')

    # --- CARREGAR (GET) ---
    # perfil recebido pela querystring (?perfil=ID) ou primeiro da lista
    perfil_id = request.GET.get('perfil') or perfis[0].id
    perfil_selecionado = get_object_or_404(Perfil, id=perfil_id)

    # busca na tabela perfis_permissoes (ManyToMany) as permissões já vinculadas
    permissoes_do_perfil = set(
        perfil_selecionado.permissoes.values_list('id', flat=True)
    )
    # agora permissoes_do_perfil é um conjunto de IDs inteiros do perfil

    context = {
        'perfis': perfis,
        'permissoes': permissoes,
        'perfil_selecionado': perfil_selecionado,
        'permissoes_do_perfil': permissoes_do_perfil,
    }
    return render(request, 'c1SuiteApp/pages/perfis_permissoes.html', context)
