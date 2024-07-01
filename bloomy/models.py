from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    company_name = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=14, null=True, blank=True)
    responsible_person = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    userFiles = models.FileField(upload_to='user_files/', null=True, blank=True)

    remaining_usages = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    def new_usage(self):
        self.remaining_usages -= 1
        self.save()
        return
    
    def has_uses_left(self):
        return self.remaining_usages > 0


class Package(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    allowed_usages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to='package_images/')

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)

    def addUsesToUser(self):
        self.user.remaining_usages += self.package.allowed_usages
        self.user.save()
        return

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'


class Specification(models.Model):
    name = models.CharField(max_length=255)
    pixel_size = models.CharField(max_length=100)
    delivery_format = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
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
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to='delivery_files/')
    
    def file_url(self):
        return self.file.url

    def __str__(self):
        return f'Delivery {self.id} for Order {self.order.id}'
