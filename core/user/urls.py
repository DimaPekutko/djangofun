from rest_framework.routers import SimpleRouter, DefaultRouter
from django.urls import path
from user.views import  RegisterViewSet, UserViewSet
from rest_framework.authtoken.views import obtain_auth_token 

router = DefaultRouter()

router.register("register", RegisterViewSet, basename="register")
router.register("", UserViewSet)

urlpatterns = [
    path('auth/', obtain_auth_token, name='auth'),
]

urlpatterns += router.urls

#  _____JWT OUTDATED LOGIC______

# # router.register("auth", LoginViewSet, basename="auth")
# router.register("refresh", RefreshTokenViewSet, basename="refresh")

# urlpatterns = []
# urlpatterns += router.urls