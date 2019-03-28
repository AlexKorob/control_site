import django_filters
from rest_framework.serializers import ValidationError
from .models import Category, Ad


class AdFilter(django_filters.FilterSet):
    price = django_filters.NumberFilter()
    price_of = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price_to = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    category = django_filters.CharFilter(method="get_category")

    def get_category(self, queryset, name, value):
        category = Category.objects.filter(name=value).first()
        if not category:
            return queryset
        return queryset.filter(category__in=Category.objects.get(name=value)\
                               .get_descendants(include_self=True))
    class Meta:
        model = Ad
        fields = ('price', )
