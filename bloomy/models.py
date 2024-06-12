from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    company_name = models.CharField(max_length=255)
    CNPJ = models.CharField(max_length=14)
    responsible_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    files = models.ManyToManyField('File')


class Package(models.Model):
    name = models.CharField(max_length=255)
    allowed_usages = models.IntegerField()
    price = models. DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Suscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL)
    start_date = models.DateTimeField(auto_now_add=True)

    def getUsesLeft():
        #IMPLEMENT
        return 0
    
    def isActive():
        if getUsesLeft() > 0: 
            return True
        else: 
            return False

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
    description = models.TextField()
    suggestedText = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    files = models.ManyToManyField('File')    
    status = models.CharField(max_length=100, choices=[
        ('EM_REVISAO', 'Em revisao'),
        ('CANCELADO', 'Cancelado'),
        ('EM_PRODUCAO', 'Em produçao'),
        ('ENTREGUE', 'Entregue')
    ])
    specification = models.ForeignKey(Specification, on_delete=models.SET_NULL)


    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class File(models.Model):
    file = models.FileField(upload_to='files/')  


class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    def __str__(self):
            return f'Delivery {self.id} for Order {self.order.id}'
