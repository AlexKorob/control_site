from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from rest_framework import generics, status
from .models import User
from rest_framework.authtoken.models import Token
from .serializers import UserCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


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
