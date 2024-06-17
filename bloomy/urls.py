from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("cliente", views.client_page, name="client_page"),
    path("packages", views.packages, name='packages'),
    path("create_order", views.create_order, name="create_order"),
    path("packages", views.packages, name="packages"),
    path("profile_form", views.profile_form, name="profile_form"),

    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout")
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)