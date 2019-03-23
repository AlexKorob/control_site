import os
from django.conf import settings
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from rest_framework import generics, status, viewsets, permissions
from .models import User, Ad, Category
from rest_framework.authtoken.models import Token
from .serializers import UserCreateSerializer, AdSerializer, CategorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser, ParseError, FormParser
from .permissions import IsCreatorOrReadOnly


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
            return HttpResponseRedirect("https://google.com/") # NOT FORGOT CHANGE

        validate = self.validate(request)
        if validate == True:
            user = User.objects.get(username=request.data["username"], password=request.data["password"])
            token_auth = "Token " + Token.objects.get(user_id=user.id).key
            return Response(token_auth)
        return Response(validate, status=status.HTTP_400_BAD_REQUEST)

    def validate(self, request):
        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return {"error": "Field username and password must be filled"}

        user = User.objects.filter(username=username, password=password)
        if not user:
            return {"error": "Username or password isn't correct"}
        return True


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly)
    # parser_classes = (MultiPartParser, FormParser)

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

    def list(self, request, *args, **kwargs):
        self.queryset = Ad.objects.filter(status=Ad.PUBLISHED)
        return super().list(self, request, *args, **kwargs)


class Categories(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
