from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    company_name = models.CharField(max_length=255, null=True, blank=True)
    CNPJ = models.CharField(max_length=14, null=True, blank=True)
    responsible_person = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    #userFiles = models.TextField(default='.')
    userFiles = models.FileField(upload_to='user_files/', null=True, blank=True)

    remaining_usages = models.IntegerField(default=0)

    def __str__(self):
        return self.username
    
    def has_usages_left(self):
        return self.remaining_usages > 0


class Package(models.Model):
    name = models.CharField(max_length=255)
    allowed_usages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)

    def getUsesLeft(self):
        return 0
    
    def isActive(self):
        return self.getUsesLeft() > 0

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'


class Specification(models.Model):
    name = models.CharField(max_length=255)
    pixel_size = models.CharField(max_length=100)
    delivery_format = models.CharField(max_length=100)

    def __str__(self):
        return f'Specification: {self.name}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    #suscripction /idk
    name = models.CharField(max_length=100)
    briefing = models.TextField()
    suggestedText = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    files = models.TextField()    
    status = models.CharField(max_length=100, choices=[
        #('EM_REVISAO', 'Em revisao'),
        ('A_FAZER', 'A fazer'),
        ('EM_PRODUCAO', 'Em produçao'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    ])
    specification = models.ForeignKey(Specification, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    

    def __str__(self):
            return f'Delivery {self.id} for Order {self.order.id}'