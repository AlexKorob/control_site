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
            except:
                raise ValidationError("Category isn't found")
        elif action == "create":
            raise ValidationError("Category field required")

        images = extra_data.get("images", None)
        if images:
            self.images_validate(images)

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
