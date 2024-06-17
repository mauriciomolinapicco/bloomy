from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

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
        model = Order #which model i build a form for
        fields = '__all__'
        exclude = ['user', 'status']