from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.producer import publish, CommandTypes
from user.models import User
from page.models import Page, Tag


def delete_user_page(request, pk):
    user = request.user
    if user.role == User.Roles.ADMIN or user.role == User.Roles.MODERATOR:
        page = get_object_or_404(Page, pk=pk)
    else:
        page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    page.delete()
    publish(CommandTypes.DELETE_PAGE, {
        "id": str(pk),
        "user_id": str(user.id)
    })
    return True, status.HTTP_200_OK


def block_user_page(request, pk):
    date = request.data["unblock_date"]
    page = get_object_or_404(Page, pk=pk)
    # if block on period
    if date:
        page.is_blocked = True
    # if block permanently
    else:
        page.is_blocked = not page.is_blocked
    page.unblock_date = date
    page.save()
    return True, status.HTTP_200_OK


def subscribe_to_page(request, pk):
    user = request.user
    page = get_object_or_404(Page, pk=pk, is_blocked=False)

    if user == page.owner:
        return "You can not subscribe to your page.", status.HTTP_400_BAD_REQUEST

    # undo actions
    if page.followers.filter(pk=user.id).exists():
        page.followers.remove(user)
        page.save()
        publish(CommandTypes.UNDO_PAGE_FOLLOWER, {"id": str(page.id)})
        return "Unsubscribed.", status.HTTP_200_OK

    elif page.follow_requests.filter(pk=user.id).exists():
        page.follow_requests.remove(user)
        page.save()
        publish(CommandTypes.UNDO_FOLLOW_REQUEST, {"id": str(page.id)})
        return "Follow request deleted.", status.HTTP_200_OK

    # create actions
    if page.is_private:
        page.follow_requests.add(request.user)
        page.save()
        publish(CommandTypes.NEW_PAGE_FOLLOW_REQUEST, {"id": str(page.id)})
        return "Follow request created.", status.HTTP_200_OK
    else:
        page.followers.add(request.user)
        page.save()
        publish(CommandTypes.NEW_PAGE_FOLLOWER, {"id": str(page.id)})
        return "Subscribed.", status.HTTP_200_OK


def request_action(request, pk):
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    req_user = get_object_or_404(User, pk=request.data["id"])

    if page.follow_requests.filter(pk=req_user.id).exists():
        page.follow_requests.remove(req_user)
        publish(CommandTypes.UNDO_FOLLOW_REQUEST, {"id": str(pk)})
        if request.data["to_approve"]:
            page.followers.add(req_user)
            page.save()
            publish(CommandTypes.NEW_PAGE_FOLLOWER, {"id": str(pk)})
            return "User added to followers.", status.HTTP_200_OK
        else:
            return "User request deleted.", status.HTTP_200_OK
    return "No such user in follow requests.", status.HTTP_400_BAD_REQUEST


def all_requests_action(request, pk):
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    to_approve = request.data["to_approve"]

    follow_requests = page.follow_requests
    for req_user in follow_requests.all():
        follow_requests.remove(req_user)
        publish(CommandTypes.UNDO_FOLLOW_REQUEST, {"id": str(pk)})
        if to_approve:
            page.followers.add(req_user)
            publish(CommandTypes.NEW_PAGE_FOLLOWER, {"id": str(pk)})
    page.save()
    if to_approve:
        msg = "All follow requests approved."
    else:
        msg = "All follow requests rejected."
    return msg, status.HTTP_200_OK


def add_tag(request, pk):
    tag_name = request.data["name"]
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    if not Tag.objects.filter(name=tag_name).exists():
        tag = Tag.objects.create(name=tag_name)
    else:
        tag = Tag.objects.get(name=tag_name)

    if page.tags.filter(name=tag_name).exists():
        return "Tag already added.", status.HTTP_400_BAD_REQUEST
    page.tags.add(tag)
    page.save()
    return "Tag added", status.HTTP_200_OK


def delete_tag(request, pk):
    tag_name = request.data["name"]
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    if not page.tags.filter(name=tag_name).exists():
        return "Error. Invalid tag.", status.HTTP_400_BAD_REQUEST
    tag = page.tags.get(name=tag_name)
    page.tags.remove(tag)
    page.save()
    return "Deleted", status.HTTP_200_OK


def set_to_private(request, pk):
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    page.is_private = True
    page.save()
    return True, status.HTTP_200_OK


def set_to_public(request, pk):
    user = request.user
    page = get_object_or_404(Page, pk=pk, owner=user, is_blocked=False)
    page.is_private = False
    page.save()
    return True, status.HTTP_200_OK


def search_pages(request):
    name = request.data["name"]
    uuid = request.data["uuid"]
    tag_name = request.data["tag_name"]
    if Tag.objects.filter(name=tag_name).exists():
        tag = Tag.objects.filter(name=tag_name)
        pages = Page.objects.filter(
            Q(name__contains=name) & Q(uuid__contains=uuid) & Q(tags__in=tag))
    else:
        pages = Page.objects.filter(
            Q(name__contains=name) & Q(uuid__contains=uuid))
    return pages.values(), status.HTTP_200_OK


def get_pages_statistics(request):
    user = request.user
    response = publish(CommandTypes.GET_ALL_STAT, {"user_id": str(user.id)})
    return response, status.HTTP_200_OK
