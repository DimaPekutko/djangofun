from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from page.serializers.post_serializers import PostCreateSerializer, PostSerializer, PostUpdateSerializer
from page.models import Post, Tag
from user.permissions import IsAdmin, IsModerator, IsPagePostOwner, IsUser
from page.services import post_service as services


class PostViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permissions_map = {
        "create": (IsUser,),
        "update": (IsPagePostOwner,),
        "liked": (IsUser,),
        "news": (IsUser,),
        "list": (IsModerator | IsAdmin,),
        "like": (IsUser | IsModerator | IsAdmin,),
        "delete": (IsPagePostOwner | IsModerator | IsAdmin,),
    }

    serializers_classes_map = {
        "create": PostCreateSerializer,
        "update": PostUpdateSerializer
    }

    def get_permissions(self):
        permissions = []
        if self.action in self.permissions_map:
            permissions = self.permissions_map[self.action]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.action in self.serializers_classes_map:
            return self.serializers_classes_map[self.action]
        return PostSerializer

    def destroy(self, request, pk):
        data, stat = services.delete_post(request, pk)
        return Response(
            data=data,
            status=stat
        )

    @action(detail=True, methods=["post"])
    def like(self, request, pk):
        data, stat = services.like_post(request, pk)
        return Response(
            data=data,
            status=stat
        )

    @action(detail=False, methods=["get"])
    def liked(self, request):
        user = request.user
        posts = user.likes.all()
        serializer = self.get_serializer_class()(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def news(self, request):
        data, stat = services.news_posts(request)
        return Response(
            data=data,
            status=stat
        )
