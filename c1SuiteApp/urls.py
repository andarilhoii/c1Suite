from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    login_view,
    logout_view,
    perfis_view,
    permissoes_view,
    usuarios_view,
    principal_view,
    perfis_permissoes_view,
)

urlpatterns = [
    path("", login_required(principal_view), name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("perfis/", login_required(perfis_view), name="perfis"),
    path("permissoes/", login_required(permissoes_view), name="permissoes"),
    path("usuarios/", login_required(usuarios_view), name="usuarios"),
    path(
        "perfis-permissoes/",
        login_required(perfis_permissoes_view),
        name="perfis_permissoes",
    ),
]

