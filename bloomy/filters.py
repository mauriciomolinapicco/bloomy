import django_filters 
from django_filters import DateFilter, CharFilter
from .models import Order

class OrderFilter(django_filters.FilterSet):
    """
    Classe para filtrar pedidos com base em critérios específicos, como data e nome.

    Atributos:
        start_date (DateFilter): Filtro para a data de início dos pedidos.
        end_date (DateFilter): Filtro para a data de término dos pedidos.
        nome (CharFilter): Filtro para o nome, permitindo uma busca por nome parcial.

    Metaclass:
        Meta: Especifica o modelo associado e os campos que podem ser filtrados.
    """
    start_date = DateFilter(field_name="date", lookup_expr='gte', label='Data desde')
    end_date = DateFilter(field_name="date", lookup_expr='lte', label='Data ate')
    nome = CharFilter(field_name='name', lookup_expr='icontains', label='Nome')

    class Meta:
        model = Order
        fields = ['status', 'user', 'nome', 'specification', 'start_date', 'end_date', 'ticket_id']