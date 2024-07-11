from django.urls import reverse
import stripe

def create_checkout_session_url(request, customer_id, price_id, package_id, user_id):
    success_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user_id),
                'package_id': str(package_id)
            },
        )

        return session.url
 
    except stripe.error.InvalidRequestError as e:
        print(f"Error de solicitud inválida en Stripe: {e}")
        raise Exception("Error al crear la sesión de checkout en Stripe.")

    except stripe.error.StripeError as e:
        print(f"Error de Stripe: {e}")
        raise Exception("Error al interactuar con Stripe.")

    except Exception as e:
        print(f"Error inesperado: {e}")
        raise Exception("Error inesperado al crear la sesión de checkout.")


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