from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'ads', views.AdViewSet, base_name="ads")
router.register(r'images', views.ImageViewSet, basename="images")
router.register(r'users', views.UserViewSet)
router.register(r'favorites', views.FavoriteViewSet, base_name="favorites")


urlpatterns = [
    path('token-auth/', obtain_auth_token),
    path('registration/', views.UserCreate.as_view(), name="user_create"),
    path('authorization/', views.UserAuthorization.as_view(), name="user_auth"),
    path('categories/', views.Categories.as_view(), name="categories"),
]

urlpatterns += router.urls
