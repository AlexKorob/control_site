from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'ads', views.AdViewSet)


urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('registration/', views.UserCreate.as_view(), name="user_create"),
    path('authorization/', views.UserAuthorization.as_view(), name="user_auth"),
    path('categories/', views.Categories.as_view(), name="categories"),
]

urlpatterns += router.urls
