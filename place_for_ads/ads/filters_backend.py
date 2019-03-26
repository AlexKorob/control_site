import coreapi
from rest_framework.filters import BaseFilterBackend
from .utils import FilterMixin
from .models import Ad


class FilterBackend(FilterMixin, BaseFilterBackend):
    def get_schema_fields(self, view):
        if view.action == "list":
            return [coreapi.Field(name='category', type='string'),
                    coreapi.Field(name='price_sort', type='string',
                                  description='enter: cheaper | expensive'),
                    coreapi.Field(name='price_of_to', type='string',
                                  description="enter: 100, 120 | 100, | ,100"), ]

        return []

    def filter_queryset(self, request, queryset, view):
        if request.method == "GET":
            category = request.GET.get("category", None)
            price = request.GET.get("price_sort", None)
            price_of_to = request.GET.get("price_of_to", None)
            if price or category or price_of_to:
                queryset = self.own_filter(category=category, price=price,
                                           price_of_to=price_of_to)
                if queryset == 400:
                    return Response("Bad Request", status=400)
            else:
                queryset = Ad.objects.filter(status=Ad.PUBLISHED)
            return queryset
        return queryset
