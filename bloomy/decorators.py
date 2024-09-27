from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def unauthenticated_user(view_func):
    """
    Decorador para restringir o acesso a usuários autenticados.

    Se o usuário estiver autenticado, redireciona para a página inicial.
    Caso contrário, permite o acesso à view fornecida.

    Parâmetros:
        view_func: A função de view que será decorada.
    """
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
    
    return wrapper_func


def allowed_users(allowed_roles=[]):
    """
    Decorador para permitir o acesso a views somente para usuários de grupos específicos.

    Verifica se o usuário pertence a um dos grupos permitidos. Se sim, permite o acesso à view.
    Caso contrário, retorna uma mensagem de erro.

    Parâmetros:
        allowed_roles: Lista de grupos permitidos para acessar a view.
        view_func: A função de view que será decorada.
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Voce nao ta autorizado a ver esta pagina')

        return wrapper_func
    return decorator

