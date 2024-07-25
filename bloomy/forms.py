from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm


class SignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=False)
    CNPJ = forms.CharField(max_length=14, min_length=14, required=False)
    responsible_person = forms.CharField(max_length=255, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    userFiles = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'company_name', 'CNPJ', 'responsible_person', 'email', 'phone_number', 'userFiles')


class OrderForm(ModelForm):
    class Meta:
        model = Order 
        fields = ('name','briefing','suggestedText', 'specification', 'file')


class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery 
        fields = ('file',) 


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('company_name', 'CNPJ', 'responsible_person', 'phone_number',)