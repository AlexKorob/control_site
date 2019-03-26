import os
from datetime import timedelta
from django.conf import settings
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from rest_framework import generics, status, viewsets, permissions
from .models import User, Ad, Category
from rest_framework.authtoken.models import Token
from .serializers import UserCreateSerializer, AdSerializer, CategorySerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser, ParseError, FormParser
from rest_framework.decorators import action
from .tasks import hide_ad_after_30_days
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

        print("authorization")
        validate = self.validate(request)
        if validate == True:
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
        list: get all or filtered ads with status == "published" 20
        create: create one ad with status == "checking" 10
        destroy: destroyed ad on id and also destroyed all images this ad from hard disk
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


class Categories(generics.ListAPIView):
    """
        list: get abstract tree categories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
        list: show all users
        retrieve: get all user ads
    """
    # lookup_field would be used by the get_object, by default == id
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    @action(detail=True, methods=("get",))
    def ad(self, request, *args, **kwargs):
        user = self.get_object()
        ad = Ad.objects.filter(creator=user)
        serializer = AdSerializer(ad, many=True)
        return Response(serializer.data)
