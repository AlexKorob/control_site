from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Ad, Category, Image
from mptt.admin import DraggableMPTTAdmin


class AdAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Category, DraggableMPTTAdmin)
admin.site.register(Image, ImageAdmin)
