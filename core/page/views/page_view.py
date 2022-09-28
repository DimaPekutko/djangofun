from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.viewsets import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from page.serializers.page_serializers import CreatePageSerializer, PageAllRequestsActionSerializer, PageBlockSerializer, PageRequestActionSerializer, PageSearchSerializer, PageSerializer, TagSerializer, UpdatePageSerializer
from page.serializers.post_serializers import PostSerializer
from page.models import Page, Post
from user.permissions import IsAdmin, IsModerator, IsPageOwner, IsUser
from user.serializers import UserSerializer
from page.services import page_service as services

class PageViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permissions_map = {
        "create": (IsUser,),
        "update": (IsPageOwner,),
        "mypages": (IsUser,),
        "subscribe": (IsUser,),
        "myposts": (IsPageOwner,),
        "add_tag": (IsPageOwner,),
        "delete_tag": (IsPageOwner,),
        "set_private": (IsPageOwner,),
        "set_public": (IsPageOwner,),
        "stat": (IsUser,),
        "list": (IsModerator | IsAdmin,),
        "block": (IsModerator | IsAdmin,),
        "delete": (IsPageOwner | IsModerator | IsAdmin,),
    }

    serializers_classes_map = {
        "create": CreatePageSerializer,
        "update": UpdatePageSerializer,
        "block": PageBlockSerializer,
        "myposts": PostSerializer,
        "request_action": PageRequestActionSerializer,
        "all_requests_action": PageAllRequestsActionSerializer,
        "add_tag": TagSerializer,
        "delete_tag": TagSerializer,
        "search": PageSearchSerializer
    }

    def get_permissions(self):
        permissions = []
        if self.action in self.permissions_map:
            permissions = self.permissions_map[self.action]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.action in self.serializers_classes_map:
            return self.serializers_classes_map[self.action]
        return PageSerializer

    def destroy(self, request, pk):
        data, stat = services.delete_user_page(request, pk)
        return Response(
            data=data,
            status=stat
        )

    @action(detail=False, methods=["get"])
    def mypages(self, request):
        pages = Page.objects.all(owner=request.user)
        serializer = self.get_serializer_class()(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def myposts(self, request, pk):
        page = get_object_or_404(Page, pk=pk, owner=request.user)
        posts = Post.objects.filter(page=page)
        serializer = self.get_serializer_class()(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"])
    def block(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, stat = services.block_user_page(request, pk)
        return Response(
            data=data,
            status=stat
        )

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk):
        data, status = services.subscribe_to_page(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["get"])
    def follow_requests(self, request, pk):
        page = get_object_or_404(
            Page, pk=pk, owner=request.user, is_blocked=False)
        serializer = UserSerializer(page.follow_requests, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def request_action(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, status = services.request_action(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["post"])
    def all_requests_action(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, status = services.all_requests_action(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["put"])
    def add_tag(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, status = services.add_tag(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["delete"])
    def delete_tag(self, request, pk):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        data, status = services.delete_tag(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["put"])
    def set_private(self, request, pk):
        data, status = services.set_to_private(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=True, methods=["put"])
    def set_public(self, request, pk):
        data, status = services.set_to_public(request, pk)
        return Response(
            data=data,
            status=status
        )

    @action(detail=False, methods=["post"])
    def search(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
        pages, status = services.search_pages(request)
        return Response(
            data=pages,
            status=status
        )

    @action(detail=False, methods=["get"])
    def stat(self, request):
        data, status = services.get_pages_statistics(request)
        return Response(
            data=data,
            status=status
        )