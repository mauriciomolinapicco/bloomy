from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_email(subject, html_content):
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = To(settings.DEFAULT_TO_EMAIL)
        content = Content("text/html", html_content)
        message = Mail(from_email, to_email, subject, content)

        response = sg.send(message)
        return response.status_code, response.body

    except Exception as e:
        return 500, str(e)
