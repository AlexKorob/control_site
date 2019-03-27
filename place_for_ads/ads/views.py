import os
from django.conf import settings
from django.shortcuts import reverse
from django.http import HttpResponseRedirect

from rest_framework import generics, status, viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User, Ad, Category, Image, Favorite
from .serializers import (UserCreateSerializer, ImageSerializer, AdSerializer, FavoriteShowSerializer,
                          CategorySerializer, UserSerializer, FavoriteSerializer)
from .permissions import IsCreatorOrReadOnly
from .filters_backend import FilterBackend


class UserCreate(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = User.objects.get(username=serializer.data["username"])
        token_auth = "Token " + Token.objects.get(user_id=user.id).key
        return Response(token_auth, status=status.HTTP_201_CREATED, headers=headers)


class UserAuthorization(APIView):
    def post(self, request):
        if request.META.get("HTTP_AUTHORIZATION", None) or request.COOKIES.get("authorization", None):
            return HttpResponseRedirect(reverse("ads-list"))

        validate = self.validate(request)
        if validate is True:
            user = User.objects.get(username=request.POST.get("username"))
            token_auth = "Token " + Token.objects.get_or_create(user=user)[0].key
            return Response(token_auth)
        return Response(validate, status=status.HTTP_400_BAD_REQUEST)

    def validate(self, request):
        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return {"error": "Field username and password must be filled"}

        user = User.objects.filter(username=username).first()

        if not user or not user.check_password(password):
            return {"error": "Username or password isn't correct"}
        return True


class AdViewSet(viewsets.ModelViewSet):
    """
        list: << get all or filtered ads with status=="published" 20 >>
        create: << create one ad with status=="checking" 10 >>
        destroy: << destroyed ad on id and also destroyed all images this ad from hard disk >>
    """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly)
    filter_backends = (FilterBackend, )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        media_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + settings.MEDIA_URL
        images = instance.images.filter(ad=instance)
        if images:
            for image in images:
                path_to_img = media_path + str(image.image)
                os.remove(str(path_to_img))
        self.perform_destroy(instance)
        return Response(f"{instance.title} was deleted", status=200)


class ImageViewSet(viewsets.ModelViewSet):
    """
        retrieve: { id specify on ad_id (not on image_id!) }
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def filter_queryset(self, queryset):
        return queryset.filter(ad__creator=self.request.user)

    def retrieve(self, request, pk=None):
        images = Image.objects.filter(ad__id=pk)
        data = []
        for image in images:
            data.append(ImageSerializer(image).data)
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        media_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + settings.MEDIA_URL
        image = instance.image
        path_to_img = media_path + str(image)

        os.remove(str(path_to_img))
        self.perform_destroy(instance)

        return Response(f"{instance.image} was deleted", status=200)


class Categories(generics.ListAPIView):
    """
        list: << get abstract tree-categories >>
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    """
        list: << show you all own favorites >>
        create: parameters: input ad id, which your are want add to favorite
        update: { input your own favorite id } parameters: id ad which you are want update;
        delete: { input your own favorite id }
    """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return FavoriteShowSerializer
        return FavoriteSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
        list: << show all users >>
    """
    # lookup_field would be used by the get_object, by default == id
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    @action(detail=True, methods=("get",))
    def ad(self, request, *args, **kwargs):
        """
            << get all user ads >>
        """
        user = self.get_object()
        ad = Ad.objects.filter(creator=user)
        serializer = AdSerializer(ad, many=True)
        return Response(serializer.data)
