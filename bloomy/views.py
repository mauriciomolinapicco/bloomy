from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from .models import Package, Subscription, User, Order, Delivery
from .util.email_util import *
from .util.payment_util import *
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


def redirect_to_payment(request, package_pk):
    if request.method == 'POST':
        
        try:
            user = request.user
            package = Package.objects.get(id=package_pk)
            
            if user.stripe_customer_id is None:
                user.create_stripe_account()
            
            print(user.stripe_customer_id)
            
            customer_id = user.stripe_customer_id
            price_id = package.stripe_product_id #check if its not none

            print(request, customer_id, price_id, package.id, user.id)
            checkout_url = create_checkout_session_url(request, customer_id, price_id, package.id, user.id)
            return redirect(checkout_url)

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao criar a inscrição: {e}")
            return redirect('packages')
        
    else:
        return render(request, "bloomy/packages.html")


def payment_success(request):
    checkout_session_id = request.GET.get('session_id', None)

    session = retrieve_checkout_session(checkout_session_id)
    if confirm_payment(session):
        user_id, package_id = extract_user_and_plan_id(session)

        user = User.objects.get(id=user_id)
        package = Package.objects.get(id=package_id)

        subscription = Subscription(
            user=user,
            package=package
        )
        subscription.save()
        subscription.addUsesToUser()
        
        return render(request, "payment/payment_success.html")
    else:
        return render(request, "payment/payment_cancel.html")


def payment_cancel(request):
    return render(request, "payment/payment_cancel.html")


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

    return render(request, "register/login.html")


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
    return render(request, "register/register.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')