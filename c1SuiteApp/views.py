from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .models import Perfil, Permissao, Usuario
from .forms import LoginForm, UsuarioForm

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
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['senha'])
            usuario.save()
            return redirect('usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios.html', {'usuarios': usuarios, 'form': form})

def principal_view(request):
    return render(request, 'c1SuiteApp/pages/principal.html')



