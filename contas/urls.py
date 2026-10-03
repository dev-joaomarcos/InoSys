from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, views_admin as a

app_name = "contas"

urlpatterns = [
    path("", views.SelecaoView.as_view(), name="selecao"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("senha/trocar/", views.TrocarSenhaView.as_view(), name="trocar_senha"),
    # administração (somente perfil Administrador)
    path("usuarios/", a.usuario_lista, name="usuario_lista"),
    path("usuarios/novo/", a.usuario_novo, name="usuario_novo"),
    path("usuarios/<int:pk>/editar/", a.usuario_editar, name="usuario_editar"),
    path("usuarios/<int:pk>/nova-senha/", a.usuario_nova_senha, name="usuario_nova_senha"),
    path("usuarios/<int:pk>/desativar/", a.usuario_desativar, name="usuario_desativar"),
    path("usuarios/<int:pk>/reativar/", a.usuario_reativar, name="usuario_reativar"),
    path("usuarios/<int:pk>/anonimizar/", a.usuario_anonimizar, name="usuario_anonimizar"),
    path("log/", a.log_lista, name="log_lista"),
]
