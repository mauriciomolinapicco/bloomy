from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from .models import Package, Subscription, User, Order, Delivery
from .util import *
from django.urls import reverse


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def complete_order(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        file = request.FILES['file']
        delivery = Delivery(
            order=order,
            file=file
        )
        delivery.save()
        order.status = 'ENTREGUE'
        order.save()

        delivered_order_email(order)

        return redirect('provider_single_order', order_id=order.id)

    return render(request, 'complete_order.html', {'order': order})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def provider_single_order(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {"order":order, "form":DeliveryForm()}
    return render(request, "bloomy/provider_single_order.html", context)


@login_required(login_url='login')
def single_order(request, order_id):
    order = order = Order.objects.get(id=order_id)
    return render(request, "bloomy/single_order.html", {"order":order})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def update_order_status(request, order_id, status):
    order = Order.objects.get(id=order_id)
    order.status = status
    order.save()
    if status == 'EM_PRODUCAO':
        order_in_progress_email(order)
    elif status == 'CANCELADO':
        order_cancelled_email(order)
    return redirect(reverse('provider_single_order', kwargs={'order_id': order_id}))


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def provider_view(request):
    orders = Order.objects.all()
    return render(request, "bloomy/provider.html", {"orders":orders})


def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    completed_orders = Order.objects.filter(user=request.user, status='ENTREGUE')
    context = {'orders':orders, 'completed_orders':completed_orders}
    return render(request, "bloomy/user_orders.html", context)


#login required
def subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, "bloomy/subscriptions.html", {'subscriptions':subscriptions})


def new_subscription(request, package_pk):
    try:
        if request.method == 'POST':
            user = request.user
            package = Package.objects.get(id=package_pk)
            subscription = Subscription(
                user=user,
                package=package
            )
            subscription.save()
            subscription.addUsesToUser()
            
            messages.success(request, 'A suscriçao foi criada com sucesso')
            #send email
    except Exception as e:   
        messages.error(request, f"Ocorreu um erro ao criar a inscrição: {e}")
    finally:
        return redirect('index') 


def package_view(request, pk):
    package = Package.objects.get(id=pk)
    return render(request, "bloomy/package.html", {"package":package})


def packages(request):
    packages = Package.objects.all()
    context = {'packages': packages}
    return render(request, 'bloomy/packages.html', context)


#@login_required
def create_order(request):

    if request.method == 'POST':
        user = request.user
        form = OrderForm(request.POST, request.FILES)

        if user.has_uses_left():
            if form.is_valid():
                
                order = form.save(commit=False)
                order.user = user
                order.status = 'A_FAZER'
                order.save()

                created_order_email(user, order)

                messages.success(request, 'Seu pedido foi carregado corretamente')
                user.new_usage()
                return redirect('/')
        else:
            messages.error(request, 'Voce nao tem usos disponiveis, pede agora seu pacote')
            return redirect('/packages')
        
    form = OrderForm()
    context = {'form':form}
    return render(request, 'bloomy/create_order.html', context)


@login_required
def profile_form(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/') 
        
    form = ProfileForm(instance=request.user)
    context = {'form':form}
    return render(request, 'bloomy/profile_form.html', context)


def packages(request):
    packages = Package.objects.all()
    context = {'packages':packages}
    return render(request, 'bloomy/packages.html',context)
 
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

    return render(request, "registration/login.html")


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            #group = Group.objects.get(name='customer')
            #user.groups.add(group)
            user.save()

            email = form.cleaned_data.get('email')
            messages.success(request, 'A conta foi criada para ' + email)

            welcome_email(email)
            return redirect('login')
    
    form = SignUpForm()
    return render(request, "registration/register.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')