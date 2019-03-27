from rest_framework.parsers import ParseError
from rest_framework.serializers import ValidationError
from .models import Category, Image, Ad


class FilterMixin(object):

    def own_filter(self, category=None, price=None, price_of_to=None):
        category = Category.objects.filter(name=category).first()

        if category is None and price is None and price_of_to is None:
            return 400

        if category:
            queryset = Ad.objects.filter(category__in=Category.objects.get(pk=category.id)\
                                         .get_descendants(include_self=True))
        else:
            queryset = Ad.objects.filter(status=Ad.PUBLISHED)

        if price:
            if price == "cheaper":
                queryset = queryset.order_by('price')
            elif price == "expensive":
                queryset = queryset.order_by('-price')
            else:
                return 400

        if price_of_to:
            if price_of_to.split(","):
                prices = price_of_to.split(",")
                try:
                    of = 0 if prices[0] == "" else float(prices[0])
                    to = 0 if prices[1] == "" else float(prices[1])
                except (ValueError, IndexError):
                    return 400
                if to == 0:
                    queryset = queryset.filter(price__gte=of)
                else:
                    queryset = queryset.filter(price__gte=of, price__lt=to)
            else:
                return 400

        return queryset
