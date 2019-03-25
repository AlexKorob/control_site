from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Ad, Category, Image
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter


class AdAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Ad._meta.fields]
    list_filter = (("category", TreeRelatedFieldListFilter), )
    search_fields = ("creator__username", "status", "title", "category__name")


class CategoryAdmin(DraggableMPTTAdmin):
    list_filter=(("parent", TreeRelatedFieldListFilter), )


class ImageAdmin(admin.ModelAdmin):
    list_display = ("ad", "image")
    list_filter = (("ad__category", TreeRelatedFieldListFilter), )
    search_fields = ("ad__creator__username", "ad__title")


admin.site.register(User, UserAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImageAdmin)
