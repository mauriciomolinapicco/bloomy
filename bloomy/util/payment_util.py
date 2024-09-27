from django.urls import reverse
import stripe

def create_checkout_session_url(request, customer_id, price_id, package_id, user_id, quantity):
    """
    Crea uma sessão de checkout no Stripe e retorna a URL para redirecionar o usuário.

    Parâmetros:
    - request: Objeto de solicitação Django.
    - customer_id: ID do cliente no Stripe.
    - price_id: ID do preço do pacote no Stripe.
    - package_id: ID do pacote no banco de dados.
    - user_id: ID do usuário que está fazendo a compra.
    - quantity: Quantidade do pacote que o usuário deseja comprar.

    Retorna:
    - URL da sessão de checkout.
    """
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
    """
    Recupera uma sessão de checkout do Stripe usando o ID da sessão.

    Parâmetros:
    - session_id: O ID da sessão de checkout a ser recuperada.

    Retorna:
    - Objeto da sessão de checkout recuperada.
    
    Levanta:
    - stripe.error.StripeError se houver um erro ao recuperar a sessão.
    """
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        raise


def confirm_payment(checkout_session):
    """
    Confirma se o pagamento foi realizado para uma sessão de checkout.

    Parâmetros:
    - checkout_session: Objeto da sessão de checkout do Stripe.

    Retorna:
    - bool: True se o pagamento foi realizado, False caso contrário.

    Levanta:
    - AttributeError se o objeto da sessão de checkout não tiver o atributo 'payment_status'.
    """
    return checkout_session.payment_status == "paid"


def extract_user_and_plan_id(checkout_session):
    """
    Extrae o ID do usuário, o ID do pacote e a quantidade dos metadados da sessão de checkout.

    Parâmetros:
    - checkout_session: Objeto da sessão de checkout do Stripe.

    Retorna:
    - tuple: Contém o ID do usuário, o ID do pacote e a quantidade.
    """
    user_id = checkout_session.metadata['user_id']
    package_id = checkout_session.metadata['package_id']
    quantity = checkout_session.metadata['quantity']
    return user_id, package_id, quantity