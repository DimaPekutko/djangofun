from django.shortcuts import get_object_or_404
from rest_framework import permissions
from page.models import Page, Post
from user.models import User


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return request.user.role == User.Roles.ADMIN
        return False


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.user.is_anonymous or user.is_blocked:
            return False
        return request.user.role == User.Roles.MODERATOR


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.user.is_anonymous:
            return False
        if user.is_blocked:
            self.message = "You are blocked by admin!"
            return False
        return request.user.role == User.Roles.USER

class IsPageOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not IsUser().has_permission(request, view):
            return False
        page_pk = view.kwargs.get("pk")
        if not Page.objects.filter(pk=page_pk, owner=user).exists():
            self.message = "You are not owner of the page!"
            return False
        return True

class IsPagePostOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not IsUser().has_permission(request, view):
            return False
        post_pk = view.kwargs.get("pk")
        post = get_object_or_404(Post, pk=post_pk)
        if not Page.objects.filter(pk=post.page.pk, owner=user).exists():
            self.message = "You are not owner of the post page!"
            return False
        return True