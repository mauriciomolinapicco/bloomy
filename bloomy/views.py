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
from .util.others_util import validate_password
from django.urls import reverse
from .filters import OrderFilter


@login_required(login_url='login')
def aprove_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'ENTREGUE'
    order.save()
    messages.success(request, "A entrega foi confirmada com sucesso")
    return redirect('user_orders')


@login_required(login_url='login')
def new_ajuste(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        
        if not order.has_ajustes_left():
            messages.error(request, "Nao tem mais ajustes disponiveis")
            return redirect('user_orders')

        form = AjusteForm(request.POST, request.FILES)
        if form.is_valid():
            ajuste = form.save(commit=False)
            ajuste.order = order
            ajuste.save()
            order.status = 'EM_AJUSTE'
            order.new_ajuste()
            order.save()
            messages.success(request, 'O ajuste foi enviado corretamente')
            return redirect('user_orders')
        
    else:
        form = AjusteForm()
    return render(request, 'bloomy/new_ajuste.html', {'form': form})


@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,'O usuario foi atualizado corretamente')
            return redirect('index')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'user/update_profile.html', {'form':form})


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
        if order.has_ajustes_left():
            order.status = 'EM_APROVACAO'
        else:
            order.status = 'ENTREGUE'
        order.save()

        delivered_order_email(order)

        return redirect('provider_single_order', order_id=order.id)
    return render(request, 'complete_order.html', {'order': order})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def provider_single_order(request, order_id):
    order = Order.objects.get(id=order_id)
    ajustes = order.ajustes.all()
    context = {"order":order, "form":DeliveryForm(), "ajustes":ajustes}
    return render(request, "bloomy/provider_single_order.html", context)


@login_required(login_url='login')
def single_order(request, order_id):
    order = order = Order.objects.get(id=order_id)
    return render(request, "bloomy/single_order.html", {"order":order})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'CANCELADO'
    order.save()
    order_cancelled_email(order)
    return redirect(reverse('provider_single_order', kwargs={'order_id': order_id}))


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def provider_view(request):
    orders = Order.objects.all().order_by('-date')
    filter = OrderFilter(request.GET, queryset=orders)
    #filter orders (filters.queryset)
    orders = filter.qs
    return render(request, "bloomy/provider.html", {"orders":orders, 'filter':filter})


@login_required(login_url='login')
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    orders_with_delivery = []
    
    for order in orders:
        recent_delivery = order.deliveries.order_by('-delivery_date').first()
        orders_with_delivery.append({
            'order': order,
            'delivery': recent_delivery
        })
    
    context = {'orders':orders, 'orders_with_delivery':orders_with_delivery}
    return render(request, "bloomy/user_orders.html", context)


@login_required(login_url='login')
def subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, "bloomy/subscriptions.html", {'subscriptions':subscriptions})


def redirect_to_payment(request, package_pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Faça login para adquirir um pacote!')
        return redirect('login')
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

        if Subscription.objects.filter(stripe_session_id=checkout_session_id).exists():
            return render(request, "payment/payment_success.html")

        
        subscription = Subscription(
            user=user,
            package=package,
            stripe_session_id=checkout_session_id
        )
        subscription.save()
        subscription.addUsesToUser()
        
        return render(request, "payment/payment_success.html")
    else:
        return render(request, "payment/payment_cancel.html")


def payment_cancel(request):
    return render(request, "payment/payment_cancel.html")


@login_required(login_url='login')
def create_order(request):

    if request.method == 'POST':
        user = request.user
        form = OrderForm(request.POST, request.FILES)

        if user.has_uses_left():
            if form.is_valid():
                order = form.save(commit=False)
                order.user = user
                order.status = 'PRODUZINDO'
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
            messages.error(request, 'Usuario ou senha incorreta')

    return render(request, "user/login.html")


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password_confirmation = request.POST.get('password2')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe')
            return render(request, 'user/register.html', {'form': form})

        elif User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já está em uso')
            return render(request, 'user/register.html', {'form': form})

        password_error = validate_password(password, password_confirmation)
        if password_error:
            messages.error(request, password_error)
            return render(request, 'user/register.html', {'form': form})
        
        if form.is_valid():
            form.save()
            messages.success(request, 'A conta foi criada para ' + email)

            welcome_email(email)
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ocurreu um erro na criacao da conta')
    else:
        form = SignUpForm()

    return render(request, "user/register.html", {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')