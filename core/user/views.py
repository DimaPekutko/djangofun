from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status
from user.permissions import IsAdmin, IsModerator, IsUser
from user.services import register_user, block_user, search_user, update_user_avatar
from user.models import User
from user.serializers import RegisterUserSerializer, UserUpdateAvatarSerializer, UserSearchSerializer, UserSerializer, UserBlockSerializer

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permissions_map = {
        "block": (IsAdmin,),
        "avatar": (IsUser | IsAdmin | IsModerator,)
    }
    serializers_classes_map = {
        "search": UserSearchSerializer,
        "set_avatar": UserUpdateAvatarSerializer
    }

    parser_classes = (MultiPartParser, JSONParser)

    def get_permissions(self):
        permissions = []
        if self.action in self.permissions_map:
            permissions = self.permissions_map[self.action]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.action in self.serializers_classes_map:
            return self.serializers_classes_map[self.action]
        return UserSerializer

    @action(detail=True, methods=["put"])
    def block(self, request, pk):
        data, stat = block_user(request, pk)
        return Response(
            data=data,
            status=stat
        )

    @action(detail=False, methods=["post"])
    def search(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, stat = search_user(request)
        s = UserSerializer(data, many=True)
        return Response(
            data=s.data,
            status=stat
        )

    @action(detail=True, methods=["put"])
    def set_avatar(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        
        data, stat = update_user_avatar(request, pk)
        return Response(
            data=data,
            status=stat
        )


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterUserSerializer

    parser_classes = (JSONParser,)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, stat = register_user(request)
        return Response(
            data=data,
            status=stat
        )


# ______JWT OUTDATED_____

# class LoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     serializer_class = LoginUserSerializer

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             return login_user(request)
#         return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)

# class RefreshTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     serializer_class = RefreshTokenSerializer

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             return rotate_tokens(request)
#         return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
