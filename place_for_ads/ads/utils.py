from rest_framework.parsers import ParseError
from rest_framework.serializers import ValidationError
from .models import Category, Image, Ad
from PIL import Image as Img

class AdSerializerMixin(object):

    def mix(self, data, context, action, instance=None):
        extra_data = dict(context.get('view').request.data.lists())
        category_name = extra_data.get("category", None)

        if category_name:
            try:
                data["category"] = Category.objects.get(name=category_name[0])
            except Category.DoesNotExist:
                raise ValidationError("Category isn't found")
        elif action == "create":
            raise ValidationError("Category field required")

        images = extra_data.get("images", None)
        if images:
            self.images_validate(images)

        if Image.objects.filter(ad=instance) and images:
            all_images = list(Image.objects.filter(ad=instance))
            all_images.extend(images)
            if len(all_images) >= 8:
                raise ValidationError("Ad must contain < 8 images")

        if action == "create":
            ad = Ad.objects.create(**data)
        else:
            ad = instance
        data["id"] = ad.id

        images_arr = []
        if images:
            for image in images:
                images_arr.append({"image": Image.objects.create(ad=ad, image=image).image})
            data["images"] = images_arr

        if action == "update" and images:
            data.pop("images")

        return data

    def images_validate(self, images):
        if len(images) >= 8:
            raise ValidationError("Images File must be < 8")
        for image in images:
            try:
                img = Img.open(image)
                img.verify()
            except:
                raise ParseError("One of upload files isn't image")
        return True


class FilterViewMixin(object):

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


def prevent_signal_save_recursion(func):
    @wraps(func)
    def no_recursion(sender, instance=None, **kwargs):
        if not instance:
            return
        if hasattr(instance, '_dirty'):
            return

        func(sender, instance=instance, **kwargs)
        try:
            instance._dirty = True
            instance.save()
        finally:
            del instance._dirty
    return no_recursion
