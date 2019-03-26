from rest_framework import permissions
from .models import Image, Ad


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator.
        return obj.creator == request.user


class IsImageCreatorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        ad_id = request.POST.get("ad", None)
        if not ad_id:
            return True

        ad = Ad.objects.filter(id=ad_id).first()

        if ad:
            return ad.creator == user
        return True
