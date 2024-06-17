from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cliente", views.client_page, name="client_page"),
    path("packages", views.packages, name='packages'),
    path("create_order", views.create_order, name="create_order"),

    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout")
    
]