from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Model de Permissão
class Permissao(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


# Model de Perfil
class Perfil(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    # ManyToMany simples: usa a tabela auto-gerada c1SuiteApp_perfil_permissoes
    permissoes = models.ManyToManyField(
        Permissao,
        blank=True,
        related_name="perfis",
    )

    def __str__(self):
        return self.nome


# Manager customizado para o usuário
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Usuário deve ter um email válido.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser deve ter is_superuser=True.")

        # Importar Perfil aqui para evitar circular import
        from .models import Perfil  # noqa

        perfil_admin, created = Perfil.objects.get_or_create(nome="Administrador")
        extra_fields.setdefault("perfil", perfil_admin)

        return self.create_user(username, email, password, **extra_fields)


# Model de Usuário customizado
class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.PROTECT)
    ativo = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UsuarioManager()

    def __str__(self):
        return self.username
