from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("packages", views.packages, name='packages'),
    path("create_order", views.create_order, name="create_order"),
    path("subscriptions", views.subscriptions, name="subscriptions"),
    path("user_orders", views.user_orders, name="user_orders"),
    path("user_orders/<str:order_id>", views.single_order, name='single_order'),
    path("provider", views.provider_view, name="provider"),
    path("provider_single_order/<str:order_id>", views.provider_single_order, name="provider_single_order"),

    path("new_subscription/<str:package_pk>", views.redirect_to_payment, name="new_subscription"),
    path("cancel_order/<str:order_id>", views.cancel_order, name="cancel_order"),
    path("complete_order/<str:order_id>", views.complete_order, name="complete_order"),
    path('new_ajuste/<str:order_id>', views.new_ajuste, name="new_ajuste"),
    path("aprove_order/<str:order_id>", views.aprove_order, name="aprove_order"),

    #user urls
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path('update_profile', views.update_profile, name="update_profile"),

    #payment urls
    path("payment_success", views.payment_success, name="payment_success"),
    path("payment_cancel", views.payment_cancel, name="payment_cancel"),

    #reset password urls
    path("reset_password/", auth_views.PasswordResetView.as_view(template_name="user/password_reset.html"), 
    name="reset_password"),

    path("reset_password_sent/", auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_sent.html"), 
    name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="user/password_reset_form.html"), 
    name="password_reset_confirm"),

    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_done.html"), 
         name="password_reset_complete"),
]