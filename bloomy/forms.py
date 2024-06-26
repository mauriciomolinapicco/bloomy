from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2') 


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('company_name', 'CNPJ', 'responsible_person', 'phone_number', 'userFiles')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['userFiles'].required = False #user files nao e requerido


class OrderForm(ModelForm):
    class Meta:
        model = Order 
        fields = ('name','briefing','suggestedText', 'specification', 'file')


class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery 
        fields = ('file',) 
