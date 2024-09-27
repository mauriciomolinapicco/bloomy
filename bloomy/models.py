from django.db import models
from django.contrib.auth.models import AbstractUser
import stripe
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Modelo que representa um usuário do sistema.

    Atributos:
    - id (UUIDField): Identificador único do usuário, gerado automaticamente.
    - company_name (CharField): Nome da empresa do usuário, se aplicável.
    - CNPJ (CharField): Cadastro Nacional da Pessoa Jurídica do usuário, se aplicável.
    - responsible_person (CharField): Nome da pessoa responsável na empresa.
    - email (EmailField): Endereço de e-mail único do usuário.
    - phone_number (CharField): Número de telefone do usuário.
    - userFiles (FileField): Arquivos enviados pelo usuário.
    - stripe_customer_id (CharField): Identificador do cliente na Stripe.
    - remaining_usages (IntegerField): Número de usos restantes do usuário.

    Métodos:
    - new_usage: Reduz o número de usos restantes em um.
    - has_uses_left: Verifica se o usuário ainda possui usos disponíveis.
    - create_stripe_account: Cria uma conta de cliente na Stripe, se ainda não existir.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=14, null=True, blank=True)
    responsible_person = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    userFiles = models.FileField(upload_to='user_files/', null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    remaining_usages = models.IntegerField(default=0)

    def __str__(self):
        """Retorna o nome de usuário como representação em string do usuário."""
        return self.username

    def new_usage(self):
        """Reduz o número de usos restantes em um e salva a alteração."""
        self.remaining_usages -= 1
        self.save()

    def has_uses_left(self):
        """Verifica se o usuário ainda tem usos disponíveis.

        Retorna:
            bool: True se houver usos restantes, caso contrário False.
        """
        return self.remaining_usages > 0

    def create_stripe_account(self):
        """Cria ou recupera uma conta de cliente na Stripe.

        Caso o cliente já exista, seu ID é recuperado e salvo no perfil do usuário.

        Lança exceções específicas caso ocorra um erro na criação ou recuperação do cliente.
        """
        try:
            customers = stripe.Customer.list(email=self.email)

            if customers.data:
                customer = customers.data[0] 
            else:
                customer = stripe.Customer.create(
                    email=self.email,
                    name=self.responsible_person,
                )

            self.stripe_customer_id = customer.id
            self.save()
        
        except stripe.error.CardError as e:
            body = e.json_body
            err  = body.get('error', {})
            print(f"Status is: {e.http_status}")
            print(f"Type is: {err.get('type')}")
            print(f"Code is: {err.get('code')}")
            raise Exception(f"Card error: {err.get('message')}")

        except stripe.error.RateLimitError as e:
            print(f"Rate limit error: {e}")
            raise Exception("Rate limit error, please try again later.")

        except stripe.error.InvalidRequestError as e:
            print(f"Invalid request: {e}")
            raise Exception("Invalid request, please check your parameters.")

        except stripe.error.AuthenticationError as e:
            print(f"Authentication error: {e}")
            raise Exception("Authentication error, please check your API keys.")

        except stripe.error.APIConnectionError as e:
            print(f"Network error: {e}")
            raise Exception("Network error, please try again.")

        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception("An error occurred, please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception("An unexpected error occurred, please try again.")


class Package(models.Model):
    """
    Modelo que representa um pacote disponível para compra.

    Atributos:
    - id (UUIDField): Identificador único do pacote, gerado automaticamente.
    - name (CharField): Nome do pacote.
    - allowed_usages (IntegerField): Número de usos permitidos para este pacote.
    - price (DecimalField): Preço do pacote, com até 10 dígitos no total e 2 casas decimais.
    - stripe_product_id (CharField): Identificador do produto na Stripe, se aplicável.

    Métodos:
    - __str__: Retorna o nome do pacote como representação em string.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    allowed_usages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_product_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Modelo que representa uma assinatura de um usuário a um pacote.

    Atributos:
    - id (UUIDField): Identificador único da assinatura, gerado automaticamente.
    - user (ForeignKey): Referência ao usuário que possui a assinatura.
    - package (ForeignKey): Referência ao pacote associado à assinatura.
    - start_date (DateTimeField): Data e hora em que a assinatura foi criada, definida automaticamente.
    - stripe_session_id (CharField): Identificador da sessão de checkout na Stripe, se aplicável.
    - quantity (IntegerField): Número de pacotes adquiridos, com validação mínima de 1 e máxima de 8.

    Métodos:
    - addUsesToUser: Adiciona os usos permitidos da assinatura ao usuário associado.
    - __str__: Retorna uma representação em string da assinatura.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )

    def addUsesToUser(self):
        """Adiciona os usos permitidos da assinatura ao usuário associado."""

        additional_uses = int(self.package.allowed_usages) * int(self.quantity)
        
        remaining_usages = int(self.user.remaining_usages)
        
        self.user.remaining_usages = remaining_usages + additional_uses
        self.user.save()
        return

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'


class Specification(models.Model):
    """
    Modelo que representa a especificação o formato das pecas, 
    por exemplo 'post de facebook'.

    Atributos:
    - id (UUIDField): Identificador único da especificação, gerado automaticamente.
    - name (CharField): Nome da especificação.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)    

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    """
    Modelo que representa um pedido feito por um usuário.

    Atributos:
    - id (UUIDField): Identificador único do pedido, gerado automaticamente.
    - user (ForeignKey): Relaciona o pedido a um usuário.
    - name (CharField): Nome do pedido.
    - briefing (TextField): Briefing do pedido.
    - suggestedText (TextField): Texto sugerido para o pedido.
    - date (DateTimeField): Data em que o pedido foi criado.
    - status (CharField): Status do pedido, com valores possíveis:
        - PRODUZINDO: Pedido em produção.
        - EM_APROVACAO: Pedido em aprovação.
        - ENTREGUE: Pedido entregue.
        - EM_AJUSTE: Pedido em ajuste.
        - CANCELADO: Pedido cancelado.
    - specification (ForeignKey): Relaciona o pedido a uma especificação.
    - file (FileField): Arquivo relacionado ao pedido.
    - for_peca_file (FileField): Arquivo adicional relacionado ao pedido.
    - pixel_size (CharField): Tamanho em pixels, se aplicável.
    - prefered_colors (CharField): Cores preferidas para o pedido.
    - ajustes_counter (IntegerField): Contador de ajustes disponíveis para o pedido.
    - ticket_id (CharField): Identificador único do ticket, gerado automaticamente.

    Métodos:
    - save: Garante que o ticket_id seja gerado antes de salvar o pedido.
    - __str__: Retorna uma representação em string do pedido.
    - new_ajuste: Adiciona um ajuste ao contador, se houver ajustes disponíveis.
    - has_ajustes_left: Verifica se ainda há ajustes disponíveis.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name = models.CharField(max_length=100)
    briefing = models.TextField()
    suggestedText = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='PRODUZINDO', choices=[
        ('PRODUZINDO', 'Produzindo'),
        ('EM_APROVACAO', 'Em aprovação'),
        ('ENTREGUE', 'Entregue'),
        ('EM_AJUSTE', 'Em ajuste'),
        ('CANCELADO', 'Cancelado'),
    ])
    specification = models.ForeignKey(Specification, on_delete=models.SET_NULL, null=True)
    file = models.FileField(null=True, blank=True, upload_to='order_files/')
    for_peca_file = models.FileField(null=True, blank=True, upload_to='for_peca_files/')
    pixel_size = models.CharField(max_length=100, null=True, blank=True)
    prefered_colors = models.CharField(max_length=100, null=True, blank=True)
    ajustes_counter = models.IntegerField(default=0)
    ticket_id = models.CharField(max_length=8, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = str(self.id).replace('-', '')[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Pedido de {self.specification} by {self.user.username}'    

    def new_ajuste(self):
        if self.ajustes_counter < 2:
            self.ajustes_counter += 1
            self.save()
        else:
            raise Exception("O usuario nao tem mais ajustes disponiveis")

    def has_ajustes_left(self):
        return self.ajustes_counter < 2


class Delivery(models.Model):
    """
    Modelo que representa a entrega de um pedido.

    Atributos:
    - id (UUIDField): Identificador único da entrega, gerado automaticamente.
    - order (ForeignKey): Relaciona a entrega a um pedido específico.
    - delivery_date (DateTimeField): Data em que a entrega foi criada.
    - file (FileField): Arquivo relacionado à entrega.

    Métodos:
    - file_url: Retorna a URL do arquivo relacionado à entrega.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    delivery_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to='delivery_files/')
    
    def file_url(self):
        return self.file.url

    def __str__(self):
        return f'Delivery {self.id} for Order {self.order.id}'
    


class Ajuste(models.Model):
    """
    Modelo que representa um ajuste realizado em um pedido.

    Atributos:
    - id (UUIDField): Identificador único do ajuste, gerado automaticamente.
    - order (ForeignKey): Relaciona o ajuste a um pedido específico.
    - description (TextField): Descrição do ajuste, limitada a 500 caracteres.
    - file (FileField): Arquivo relacionado ao ajuste.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ajustes')
    description = models.TextField(max_length=500)
    file = models.FileField(null=True, blank=True, upload_to='ajustes_files/')

    def __str__(self):
        return f'Ajuste do pedido {self.order.__str__}'