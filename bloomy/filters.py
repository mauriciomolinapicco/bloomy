import django_filters 
from django_filters import DateFilter, CharFilter
from .models import Order

class OrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="date", lookup_expr='gte', label='Data desde')
    end_date = DateFilter(field_name="date", lookup_expr='lte', label='Data ate')
    nome = CharFilter(field_name='name', lookup_expr='icontains', label='Nome')

    class Meta:
        model = Order
        fields = ['status', 'user', 'nome', 'specification', 'start_date', 'end_date', 'ticket_id']