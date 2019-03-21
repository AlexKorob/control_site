from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('registration/', views.UserCreate.as_view(), name="user_create"),
    path('authorization/', views.UserAuthorization.as_view(), name="user_auth"),

]
