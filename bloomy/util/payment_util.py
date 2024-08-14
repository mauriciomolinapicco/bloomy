from django.urls import reverse
import stripe

def create_checkout_session_url(request, customer_id, price_id, package_id, user_id, quantity):
    success_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': quantity,
            }],
            mode='payment',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user_id),
                'package_id': str(package_id),
                'quantity': quantity
            },
        )

        return session.url
 
    except stripe.error.InvalidRequestError as e:
        print(f"Erro de solicitação inválida no Stripe: {e}")
        raise Exception("Erro ao criar a sessão de checkout no Stripe.")

    except stripe.error.StripeError as e:
        print(f"Erro do Stripe: {e}")
        raise Exception("Erro ao interagir com o Stripe.")

    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise Exception("Erro inesperado ao criar a sessão de checkout.")


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
        quantity = checkout_session.metadata['quantity']
        return user_id, package_id, quantity