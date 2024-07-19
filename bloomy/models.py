from django.db import models
from django.contrib.auth.models import AbstractUser
import stripe
import uuid

class User(AbstractUser):
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
        return self.username

    def new_usage(self):
        self.remaining_usages -= 1
        self.save()
        return
    
    def has_uses_left(self):
        return self.remaining_usages > 0
    

    def create_stripe_account(self):
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
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    allowed_usages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_product_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)

    def addUsesToUser(self):
        self.user.remaining_usages += self.package.allowed_usages
        self.user.save()
        return

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'


class Specification(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    pixel_size = models.CharField(max_length=100)
    delivery_format = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name = models.CharField(max_length=100)
    briefing = models.TextField()
    suggestedText = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='A_FAZER', choices=[
        ('A_FAZER', 'A fazer'),
        ('EM_PRODUCAO', 'Em produçao'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    ])
    specification = models.ForeignKey(Specification, on_delete=models.SET_NULL, null=True)
    file = models.FileField(null=True, blank=True, upload_to='order_files/')

    def __str__(self):
        return f'ID:{self.id} | Pedido de {self.specification} by {self.user.username}'


class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to='delivery_files/')
    
    def file_url(self):
        return self.file.url

    def __str__(self):
        return f'Delivery {self.id} for Order {self.order.id}'
