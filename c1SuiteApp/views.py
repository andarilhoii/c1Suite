from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .models import Perfil, Permissao, Usuario, ParceiroTipo
from .forms import LoginForm, UsuarioForm
from django.urls import reverse       
from django.contrib import messages   
from django.db import IntegrityError

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
    # ----- PERMISSÕES DO PERFIL DO USUÁRIO LOGADO -----
    user = request.user
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )
    
    # ---------- CREATE / UPDATE ----------
    if request.method == "POST" and request.POST.get("acao") == "salvar":
        # se não tiver a permissão, não salva
        if "PERFIS_SUB_SALVAR" not in permissoes_nomes:
            return redirect("perfis")

        perfil_id = request.POST.get("id")
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao", "")

        if perfil_id:  # atualização
            # se quiser, pode exigir PERFIS_SUB_EDITAR aqui
            perfil = get_object_or_404(Perfil, id=perfil_id)
            perfil.nome = nome
            perfil.descricao = descricao
            perfil.save()
        else:  # inclusão
            Perfil.objects.create(nome=nome, descricao=descricao)

        return redirect("perfis")

    # ---------- DELETE ----------
    if request.method == "POST" and request.POST.get("acao") == "excluir":
        if "PERFIS_SUB_EXCLUIR" not in permissoes_nomes:
            return redirect("perfis")

        perfil_id = request.POST.get("id")
        perfil = get_object_or_404(Perfil, id=perfil_id)
        perfil.delete()
        return redirect("perfis")

    # ---------- EDIT (carregar dados no form) ----------
    perfil_editar = None
    perfil_id = request.GET.get("editar")
    if perfil_id and "PERFIS_SUB_EDITAR" in permissoes_nomes:
        perfil_editar = get_object_or_404(Perfil, id=perfil_id)

    perfis = Perfil.objects.all().order_by("nome")
    return render(
        request,
        "c1SuiteApp/pages/perfis.html",
        {
            "perfis": perfis,
            "perfil_editar": perfil_editar,
            "permissoes_nomes": permissoes_nomes,
        },
    )

def permissoes_view(request):
    # ----- PERMISSÕES DO PERFIL DO USUÁRIO LOGADO -----
    user = request.user
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )

    # ----- CREATE / UPDATE -----
    if request.method == "POST" and request.POST.get("acao") == "salvar":
        # se o perfil tiver PERFIS_SUB_SALVAR, ele pode incluir/alterar permissões
        if "PERFIS_SUB_SALVAR" not in permissoes_nomes:
            return redirect("permissoes")

        permissoes_id = request.POST.get("id")
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()

        # inclusão de nova permissão
        if not permissoes_id:
            Permissao.objects.create(nome=nome, descricao=descricao)
        else:
            # atualização de permissão já existente
            permissao = get_object_or_404(Permissao, id=permissoes_id)
            permissao.nome = nome
            permissao.descricao = descricao
            permissao.save()

        # Sempre redireciona SEM contexto de edição (form volta vazio)
        return redirect("permissoes")

    # ----- DELETE -----
    if request.method == "POST" and request.POST.get("acao") == "excluir":
        # Se quiser controlar exclusão, coloque checagem de permissão aqui
        permissoes_id = request.POST.get("id")
        permissao = get_object_or_404(Permissao, id=permissoes_id)
        permissao.delete()
        return redirect("permissoes")

    # ----- EDIT (carregar dados no form) - GET ?editar=ID -----
    permissao_editar = None
    permissoes_id = request.GET.get("editar")
    if permissoes_id:
        # Se quiser, condicione aqui a uma permissão de edição
        permissao_editar = get_object_or_404(Permissao, id=permissoes_id)

    # Lista para a tabela
    permissoes = Permissao.objects.all().order_by("nome")

    return render(
        request,
        "c1SuiteApp/pages/permissoes.html",  # mantém o caminho que funciona no seu projeto
        {
            "permissoes": permissoes,
            "permissoes_editar": permissao_editar,
            "permissoes_nomes": permissoes_nomes,
        },
    )

def usuarios_view(request):
    usuarios = Usuario.objects.all()
    perfis = Perfil.objects.all().order_by("nome")

    # permissões do usuário logado (se estiver usando no template)
    user = request.user
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )

    editar_id = request.GET.get("editar")

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

            # aqui pode validar permissão: "USUARIO_SUB_EXCLUIR" in permissoes_nomes
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
            usuario_id_form = request.POST.get("usuario_id")

            if usuario_id_form:
                usuario = get_object_or_404(Usuario, pk=int(usuario_id_form))
            else:
                usuario = Usuario()

            usuario.username = username
            usuario.email = email
            usuario.set_password(senha)
            usuario.ativo = ativo
            usuario.perfil_id = perfil_id

            try:
                usuario.save()
                messages.success(request, "Usuário salvo com sucesso.")
                return redirect(reverse("usuarios"))
            except IntegrityError:
                messages.error(request, "Já existe um usuário com esse login.")

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
            "permissoes_nomes": permissoes_nomes,
        },
    )

def principal_view(request):
    user = request.user # já vem autenticado por login_required

    # Se o usuário tiver perfil associado, pega os nomes das permissões
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )
    context = {
        "permissoes_nomes": permissoes_nomes
    }

    return render(request, 'c1SuiteApp/pages/principal.html', context)
    
def perfis_permissoes_view(request):
    perfis = Perfil.objects.all().order_by('nome')
    permissoes = Permissao.objects.all().order_by('nome')

    # permissões do perfil do usuário logado
    user = request.user
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )

    if not perfis:
        return render(request, 'c1SuiteApp/pages/perfis_permissoes.html', {
            'perfis': [],
            'permissoes': permissoes,
            'perfil_selecionado': None,
            'permissoes_do_perfil': [],
            'permissoes_nomes': permissoes_nomes,
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

    # permissões já vinculadas ao perfil selecionado
    permissoes_do_perfil = set(
        perfil_selecionado.permissoes.values_list('id', flat=True)
    )

    context = {
        'perfis': perfis,
        'permissoes': permissoes,
        'perfil_selecionado': perfil_selecionado,
        'permissoes_do_perfil': permissoes_do_perfil,
        'permissoes_nomes': permissoes_nomes,  # usado no template para habilitar o botão
    }
    return render(request, 'c1SuiteApp/pages/perfis_permissoes.html', context)

#------------------ views cadastros

def parceiros_tipo_view(request):
    # ----- PERMISSÕES DO PERFIL DO USUÁRIO LOGADO -----
    user = request.user
    permissoes_nomes = set()
    if hasattr(user, "perfil") and user.perfil is not None:
        permissoes_nomes = set(
            user.perfil.permissoes.values_list("nome", flat=True)
        )

    # ----- CREATE / UPDATE -----
    if request.method == "POST" and request.POST.get("acao") == "salvar":
        if "CAD_PAR_TIPO_SUB_SALVAR" not in permissoes_nomes:
            return redirect("tipos_parceiros")

        tipo_id = request.POST.get("id")
        descricao = request.POST.get("descricao", "").strip()

        if tipo_id:  # atualização
            tipo = get_object_or_404(ParceiroTipo, id_tipopar=tipo_id)
            tipo.descricao = descricao
            tipo.save()
        else:        # inclusão
            ParceiroTipo.objects.create(descricao=descricao)

        return redirect("tipos_parceiros")

    # ----- DELETE -----
    if request.method == "POST" and request.POST.get("acao") == "excluir":
        if "CAD_PAR_TIPO_SUB_EXCLUIR" not in permissoes_nomes:
            return redirect("tipos_parceiros")

        tipo_id = request.POST.get("id")
        tipo = get_object_or_404(ParceiroTipo, id_tipopar=tipo_id)
        tipo.delete()
        return redirect("tipos_parceiros")

    # ----- EDIT (carregar dados no form) -----
    tipo_editar = None
    tipo_id = request.GET.get("editar")
    if tipo_id and "CAD_PAR_TIPO_SUB_EDITAR" in permissoes_nomes:
        tipo_editar = get_object_or_404(ParceiroTipo, id_tipopar=tipo_id)

    tipos = ParceiroTipo.objects.all().order_by("descricao")

    return render(
        request,
        "c1SuiteApp/pages/parceiros_tipo.html",
        {
            "tipos": tipos,
            "tipo_editar": tipo_editar,
            "permissoes_nomes": permissoes_nomes,
        },
    )
