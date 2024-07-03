from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content, To
import os 
from dotenv import load_dotenv
from django.template.loader import render_to_string
import stripe
from django.urls import reverse

load_dotenv()

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


def create_checkout_session_url(request, customer_id, price_id, package_id, user_id):
    success_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
    print('paso')
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
                'user_id': str(user_id), 'package_id': str(package_id)},
    )

    return session.url


def retrieve_checkout_session(session_id):
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            raise


def confirm_payment(checkout_session):
    return checkout_session.payment_status == "paid"


def extract_user_and_plan_id(checkout_session):
        user_id = checkout_session.metadata['user_id']
        package_id = checkout_session.metadata['package_id']
        return user_id, package_id