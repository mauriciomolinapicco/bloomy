from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users
from .models import Package, Subscription, User, Order, Delivery
from .util.email_util import *
from .util.payment_util import *
from .util.others_util import validate_password, validate_quantity
from django.urls import reverse
from .filters import OrderFilter
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.core.exceptions import ValidationError


@login_required(login_url='login')
def aprove_order(request, order_id):
    """
    View para aprovar e marcar um pedido como entregue.

    Esta view lida com o processo de atualização do status de um pedido para "ENTREGUE" 
    com base no order_id fornecido. Se o pedido existir, o status é atualizado, e 
    uma mensagem de sucesso é exibida ao usuário.

    Parâmetros:
    order_id (int): O ID do pedido a ser aprovado.

    Retorna:
    HttpResponseRedirect: Redireciona o usuário para a página de pedidos do usuário após
    a atualização do status.
    """
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'ENTREGUE'
    order.save()
    messages.success(request, "A entrega foi confirmada com sucesso")
    return redirect('user_orders')


@login_required(login_url='login')
def new_ajuste(request, order_id):
    """
    View para criar e enviar um novo ajuste para um pedido.

    Esta view permite que o usuário envie um ajuste para um pedido específico. 
    Verifica se ainda há ajustes disponíveis para o pedido e, se sim, permite o envio 
    do ajuste por meio de um formulário. Ao submeter o ajuste com sucesso, o status 
    do pedido é atualizado para "EM_AJUSTE", e e-mails são enviados tanto ao administrador 
    quanto ao usuário.

    Parâmetros:
    order_id (int): O ID do pedido para o qual será enviado o ajuste.

    Retorna:
    HttpResponseRedirect: Redireciona o usuário para a página de pedidos do usuário após o envio.
    HttpResponse: Renderiza a página de envio de ajuste se a requisição for GET.
    """
    order = get_object_or_404(Order, pk=order_id)
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
            new_ajuste_email_admin(ajuste)
            new_ajuste_email_user(ajuste)
            return redirect('user_orders')
        
    else:
        form = AjusteForm()
    return render(request, 'bloomy/new_ajuste.html', {'form': form})


@login_required(login_url='login')
def update_profile(request):
    """
    View para atualizar o perfil do usuário.

    Esta view permite que o usuário atualize as informações do seu perfil por meio de um formulário.
    Se o formulário for enviado e válido, as informações são salvas e uma mensagem de sucesso é exibida.

    Retorna:
    HttpResponseRedirect: Redireciona o usuário para a página principal após a atualização.
    HttpResponse: Renderiza a página de atualização de perfil se a requisição for GET.
    """

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
    """
    View para completar um pedido com o envio de um arquivo de entrega.

    Esta view permite que o administrador ou o usuário autorizado envie o arquivo final 
    de entrega para um pedido específico. Após o upload, o status do pedido é atualizado
    de acordo com o número de ajustes restantes.

    Parâmetros:
    order_id (int): O ID do pedido a ser completado.

    Retorna:
    HttpResponseRedirect: Redireciona para a página do pedido após a entrega ser concluída.
    HttpResponse: Renderiza a página de conclusão de pedido se a requisição for GET.
    """
    order = Order.objects.get(id=order_id)    
    if request.method == 'POST':
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
    """
    View para exibir um pedido específico para o provedor.

    Mostra as informações detalhadas de um pedido, incluindo os ajustes e o formulário de entrega.

    Parâmetros:
    order_id (int): O ID do pedido a ser exibido.

    Retorna:
    HttpResponse: Página com os detalhes do pedido para o provedor.
    """
    order = Order.objects.get(id=order_id)
    ajustes = order.ajustes.all()
    context = {"order":order, "form":DeliveryForm(), "ajustes":ajustes}
    return render(request, "bloomy/provider_single_order.html", context)


@login_required(login_url='login')
def single_order(request, order_id):
    """
    View para exibir um pedido específico para o usuário.

    Verifica se o pedido pertence ao usuário atual e exibe os detalhes do pedido, 
    incluindo as entregas e o número de ajustes restantes.

    Parâmetros:
    order_id (int): O ID do pedido a ser exibido.

    Retorna:
    HttpResponse: Página com os detalhes do pedido para o usuário.
    """
    order = get_object_or_404(Order, id=order_id)
    if request.user != order.user:
        return redirect('user_orders')

    delivery = order.deliveries.order_by('-delivery_date').first()
    context = {"order":order, "remaining_ajustes": 2 - order.ajustes_counter, "delivery":delivery}
    return render(request, "bloomy/single_order.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def cancel_order(request, order_id):
    """
    View para cancelar um pedido.

    Altera o status do pedido para "CANCELADO" e envia um e-mail notificando o cancelamento.

    Parâmetros:
    order_id (int): O ID do pedido a ser cancelado.

    Retorna:
    HttpResponseRedirect: Redireciona para a página de pedido do provedor após o cancelamento.
    """
    order = get_object_or_404(Order, id=order_id)
    order.status = 'CANCELADO'
    order.save()
    order_cancelled_email(order)
    return redirect(reverse('provider_single_order', kwargs={'order_id': order_id}))


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def provider_view(request):
    """
    View para exibir e filtrar os pedidos para o provedor.

    Mostra uma lista de todos os pedidos, ordenados por data, com a possibilidade 
    de filtragem e paginação. Os parâmetros do filtro são mantidos na paginação.

    Retorna:
    HttpResponse: Página com a lista de pedidos filtrados e paginados.
    """
    orders = Order.objects.all().order_by('-date')

    filter = OrderFilter(request.GET, queryset=orders)
    orders = filter.qs

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pasar los parámetros del filtro a la plantilla
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, "bloomy/provider.html", {"orders": orders, 'filter': filter, 'page_obj': page_obj, 'query_string': query_string})


@login_required(login_url='login')
def user_orders(request):
    """
    View para exibir os pedidos do usuário.

    Mostra a lista de pedidos do usuário atual, ordenados por data, e coleta as entregas mais recentes 
    dos pedidos com status 'ENTREGUE'.

    Retorna:
    HttpResponse: Página com a lista de pedidos e entregas recentes do usuário.
    """
    orders = Order.objects.filter(user=request.user).order_by('-date')

    delivered_orders = Order.objects.filter(user=request.user, status='ENTREGUE')
    deliveries = []
    for order in delivered_orders:
        latest_delivery = order.deliveries.order_by("-delivery_date").first()
        if latest_delivery:
            deliveries.append(latest_delivery)
    
    context = {'orders':orders, 'deliveries':deliveries}
    return render(request, "bloomy/user_orders.html", context)


@login_required(login_url='login')
def subscriptions(request):
    """
    View para exibir as assinaturas do usuário.

    Mostra a lista de assinaturas ativas e anteriores do usuário, ordenadas pela data de início.

    Retorna:
    HttpResponse: Página com a lista de assinaturas do usuário.
    """
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-start_date')
    return render(request, "bloomy/subscriptions.html", {'subscriptions':subscriptions})


def redirect_to_payment(request, package_pk):
    """
    View para redirecionar o usuário para a página de pagamento.

    Verifica se o usuário está autenticado e, em caso afirmativo, tenta criar uma sessão de checkout 
    para o pacote selecionado. Se o usuário não tiver uma conta Stripe, uma nova conta é criada. 
    O método aceita requisições POST para iniciar o pagamento.

    Parâmetros:
    package_pk (int): O ID do pacote a ser adquirido.

    Retorna:
    HttpResponseRedirect: Redireciona para a página de checkout ou para a lista de pacotes.
    HttpResponse: Renderiza a página de pacotes se a requisição for GET.
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Faça login para adquirir um pacote!')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            user = request.user
            package = Package.objects.get(id=package_pk)
            quantity = request.POST.get('quantity', 1)
            try:
                validate_quantity(quantity)
            except ValidationError as e:
                return redirect('packages')

            if user.stripe_customer_id is None:
                user.create_stripe_account()
            
            customer_id = user.stripe_customer_id
            price_id = package.stripe_product_id #check if its not none

            if price_id is not None:
                checkout_url = create_checkout_session_url(request, customer_id, price_id, package.id, user.id, quantity)
                return redirect(checkout_url)
            return redirect('packages')

        except Exception as e:
            return redirect('packages')
        
    else:
        return render(request, "bloomy/packages.html")


def payment_success(request):
    """
    View para tratar o sucesso do pagamento.

    Verifica o status da sessão de checkout e, se o pagamento for confirmado, 
    cria uma nova assinatura para o usuário e envia um e-mail de confirmação. 
    Caso contrário, renderiza a página de cancelamento do pagamento.

    Retorna:
    HttpResponse: Renderiza a página de sucesso ou cancelamento do pagamento.
    """
    checkout_session_id = request.GET.get('session_id', None)

    session = retrieve_checkout_session(checkout_session_id)
    if confirm_payment(session):
        user_id, package_id, quantity = extract_user_and_plan_id(session)

        user = User.objects.get(id=user_id)
        package = Package.objects.get(id=package_id)

        if Subscription.objects.filter(stripe_session_id=checkout_session_id).exists():
            return render(request, "payment/payment_success.html")

        
        subscription = Subscription(
            user=user,
            package=package,
            stripe_session_id=checkout_session_id,
            quantity=quantity
        )
        subscription.save()
        subscription.addUsesToUser()

        #Send email
        payment_success_email(subscription)

        
        return render(request, "payment/payment_success.html")
    else:
        return render(request, "payment/payment_cancel.html")


def payment_cancel(request):
    """
    View para renderizar a página de cancelamento de pagamento.

    Retorna:
    HttpResponse: Página que informa ao usuário sobre o cancelamento do pagamento.
    """
    return render(request, "payment/payment_cancel.html")


@login_required(login_url='login')
def create_order(request):
    """
    View para criar um novo pedido.

    Verifica se o usuário tem usos disponíveis e, em caso afirmativo, 
    processa o formulário de pedido. Se o pedido for salvo com sucesso, 
    um e-mail de confirmação é enviado e o uso do usuário é atualizado.

    Retorna:
    HttpResponse: Redireciona para a página inicial após a criação do pedido 
                  ou renderiza o formulário de criação de pedido.
    """
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
    """
    View para exibir todos os pacotes disponíveis.

    Recupera todos os pacotes ordenados pelo número de usos permitidos e 
    renderiza a página de pacotes.

    Retorna:
    HttpResponse: Página com a lista de pacotes disponíveis.
    """
    packages = Package.objects.all().order_by('allowed_usages')
    context = {'packages':packages}
    return render(request, 'bloomy/packages.html',context)
 
def index(request):
    """
    View para renderizar a página inicial.

    Retorna:
    HttpResponse: Página inicial da aplicação.
    """
    return render(request, 'bloomy/index.html')


@unauthenticated_user
def login_view(request):
    """
    View para processar o login do usuário.

    Verifica se a requisição é do tipo POST e, em caso afirmativo, 
    tenta autenticar o usuário com o nome de usuário e senha fornecidos. 
    Se a autenticação for bem-sucedida, o usuário é redirecionado para 
    a página inicial; caso contrário, uma mensagem de erro é exibida.

    Retorna:
    HttpResponse: Renderiza a página de login ou redireciona para a página inicial.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuario ou senha incorreta')

    return render(request, "user/login.html")


@unauthenticated_user
def register(request):
    """
    View para registrar um novo usuário.

    Processa o formulário de registro e realiza as validações necessárias, 
    como verificar se o nome de usuário ou e-mail já estão em uso e validar 
    as senhas. Se o registro for bem-sucedido, uma mensagem de sucesso é exibida 
    e o usuário é redirecionado para a página de login.

    Retorna:
    HttpResponse: Renderiza a página de registro ou redireciona para a página de login.
    """
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
    """
    View para processar o logout do usuário.

    Realiza o logout do usuário autenticado e redireciona para a página de login.

    Retorna:
    HttpResponse: Redireciona para a página de login após o logout.
    """
    logout(request)
    return redirect('login')