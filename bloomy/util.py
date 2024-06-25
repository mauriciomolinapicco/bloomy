from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os 
from dotenv import load_dotenv
from django.template.loader import render_to_string

load_dotenv()
#SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
def send_email(to_emails, subject, html_content):
    message = Mail(
        from_email='fabricio@rooster.dev.br', 
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
    admin_email = 'mauricio.molina@rooster.dev.br'
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


def welcome_email(user_email):
    subject = "Bem-vindo ao Bloomy"
    html_content = render_to_string('emails/welcome_email.html')
    send_email(user_email, subject, html_content)


def delivered_order_email(order):
    subject = "Trabalho disponível para visualização"
    to_emails = order.user.email
    html_content = render_to_string('emails/delivered_order_email.html')
    send_email(to_emails, subject, html_content)


def order_in_progress_email(order):
    subject = "Ordem em progresso"
    html_content = render_to_string('emails/order_in_progress_email.html', {'order': order})
    to_emails = order.user.email
    send_email(to_emails, subject, html_content)


def order_cancelled_email(order):
    subject = "Ordem cancelada"
    html_content = render_to_string('emails/order_cancelled_email.html', {'order': order})
    to_emails = order.user.email
    send_email(to_emails, subject, html_content)