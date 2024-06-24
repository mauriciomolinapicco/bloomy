from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("cliente", views.client_page, name="client_page"),
    path("packages", views.packages, name='packages'),
    path("packages/<str:pk>", views.package_view, name='package_view'),
    path("create_order", views.create_order, name="create_order"),
    path("profile_form", views.profile_form, name="profile_form"),
    path("subscriptions", views.subscriptions, name="subscriptions"),
    path("user_orders", views.user_orders, name="user_orders"),
    path("user_orders/<str:order_id>", views.single_order, name='single_order'),
    path("provider", views.provider_view, name="provider"),

    path("new_subscription/<str:package_pk>", views.new_subscription, name="new_subscription"),
    path("order_in_progress/<str:order_id>", views.order_in_progress, name="order_in_progress"),

    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout")
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)