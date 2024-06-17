from django.shortcuts import render, redirect
from .forms import SignUpForm, OrderForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from .models import Package

'''def packages(request):
    packages = Package.objects.all()
    context = {'packages':packages}
    return render(request, 'bloomy/packages.html',context)'''


def create_order(request):
    form = OrderForm()
    context = {'form':form}

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/') 


    return render(request, 'bloomy/order_form.html', context)


def packages(request):
    packages = Package.objects.all()
    context = {'packages':packages}
    return render(request, 'bloomy/packages.html',context)


def client_page(request):
    return render(request, 'bloomy/cliente.html')


@login_required(login_url='login')
@allowed_users(allowed_roles=['fornecedor'])
def index(request):
    return render(request, 'bloomy/index.html')


@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Usuario ou senha incorreta')

    return render(request, "bloomy/login.html")


@unauthenticated_user
def register(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, 'A conta foi criada para ' + email)
            return redirect('login')  # Cambia 'login' por el nombre de tu URL de redirección para el login
    
    form = SignUpForm()
    return render(request, "bloomy/register.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')