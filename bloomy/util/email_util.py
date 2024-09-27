from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content, To
import os 
from dotenv import load_dotenv
from django.template.loader import render_to_string

load_dotenv()

def send_email(to_emails, subject, html_content):
    """
    Envia um email usando a API do SendGrid.

    Esta função cria e envia um email para os endereços de email fornecidos
    com o assunto e conteúdo HTML especificados.

    Args:
        to_emails (list): Uma lista de endereços de email para os quais o email será enviado.
        subject (str): O assunto do email.
        html_content (str): O conteúdo HTML do email.

    Returns:
        None: Não retorna nada, mas imprime o status do envio do email.

    Raises:
        Exception: Levanta uma exceção se houver um erro ao enviar o email.
    """
    message = Mail(
        from_email='bloomy@rooster.dev.br', 
        to_emails=to_emails,
        subject=subject,
        html_content=html_content)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print('Email enviado exitosamente')
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print('Error al enviar el email')
        print(str(e))


def created_order_email(user, order):
    """
    Envia emails de confirmação de pedido para o usuário e o administrador.

    Esta função gera e envia dois emails: um para o administrador informando
    sobre um novo pedido e outro para o usuário confirmando que seu pedido
    foi enviado corretamente.

    Args:
        user (User): O objeto do usuário que fez o pedido.
        order (Order): O objeto do pedido que foi criado.

    Returns:
        None: Não retorna nada, mas envia dois emails.

    Raises:
        Exception: Levanta uma exceção se houver um erro ao enviar os emails.
    """
    admin_email = 'contato@pinacriacao.com'
    user_email = user.email

    subject_admin = "Novo pedido"
    context_admin = {
        'order': order,
        'user': user,
    }
    html_content_admin = render_to_string('emails/created_order_email_admin.html', context_admin)
    send_email(admin_email, subject_admin, html_content_admin)

    subject_user = "Pedido corretamente enviado"
    context_user = {
        'order': order,
        'user': user,
    }
    html_content_user = render_to_string('emails/created_order_email_user.html', context_user)
    send_email(user_email, subject_user, html_content_user)


def payment_success_email(subscription):
    """
    Envia um email de confirmação de compra para o usuário após um pagamento bem-sucedido.

    Args:
        subscription (Subscription): O objeto de assinatura relacionado à compra.

    Returns:
        None: Não retorna nada, mas envia um email de confirmação.
    """
    subject = "Confirmação de Compra"
    email = subscription.user.email
    context = {'subscription': subscription}
    html_content = render_to_string("emails/payment_success_email.html", context)
    send_email(email, subject, html_content)


def new_ajuste_email_user(ajuste):
    """
    Envia um email ao usuário informando que um ajuste foi enviado com sucesso.

    Args:
        ajuste (Ajuste): O objeto de ajuste que foi enviado.

    Returns:
        None: Não retorna nada, mas envia um email ao usuário.
    """
    subject = "Ajuste enviado com sucesso"
    email = ajuste.order.user.email
    context = {'ajuste': ajuste}
    html_content = render_to_string("emails/new_ajuste_email_user.html", context)
    send_email(email, subject, html_content)


def new_ajuste_email_admin(ajuste):
    """
    Envia um email para o administrador notificando que um novo ajuste foi criado.

    Args:
        ajuste (Ajuste): O objeto de ajuste que foi criado.

    Returns:
        None: Não retorna nada, mas envia um email ao administrador.
    """
    subject = "Novo ajuste na bloomy"
    email = 'contato@pinacriacao.com'
    context = {'ajuste': ajuste}
    html_content = render_to_string("emails/new_ajuste_email_admin.html", context)
    send_email(email, subject, html_content)


def welcome_email(user_email):
    """
    Envia um email de boas-vindas ao novo usuário após o registro.

    Args:
        user_email (str): O endereço de email do novo usuário.

    Returns:
        None: Não retorna nada, mas envia um email de boas-vindas.
    """
    subject = "Bem-vindo ao Bloomy"
    html_content = render_to_string('emails/welcome_email.html')
    send_email(user_email, subject, html_content)


def delivered_order_email(order):
    """
    Envia um email ao usuário informando que o trabalho está disponível para visualização.

    Args:
        order (Order): O objeto do pedido que foi entregue.

    Returns:
        None: Não retorna nada, mas envia um email ao usuário.
    """
    subject = "Trabalho disponível para visualização"
    to_emails = order.user.email
    html_content = render_to_string('emails/delivered_order_email.html')
    send_email(to_emails, subject, html_content)


def order_in_progress_email(order):
    """
    Envia um email ao usuário notificando que o pedido está em progresso.

    Args:
        order (Order): O objeto do pedido que está sendo processado.

    Returns:
        None: Não retorna nada, mas envia um email ao usuário.
    """
    subject = "Ordem em progresso"
    html_content = render_to_string('emails/order_in_progress_email.html', {'order': order})
    to_emails = order.user.email
    send_email(to_emails, subject, html_content)


def order_cancelled_email(order):
    """
    Envia um email ao usuário informando que o pedido foi cancelado.

    Args:
        order (Order): O objeto do pedido que foi cancelado.

    Returns:
        None: Não retorna nada, mas envia um email ao usuário.
    """
    subject = "Ordem cancelada"
    html_content = render_to_string('emails/order_cancelled_email.html', {'order': order})
    to_emails = order.user.email
    send_email(to_emails, subject, html_content)
