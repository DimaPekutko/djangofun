from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.producer import publish, CommandTypes
from user.models import User
from page.models import Page, Post
from page.tasks import notify_follower_about_new_post

def create_post(request):
    page_id = request.data["page"]
    content = request.data["content"]

    user = request.user
    page = None
    # in case new post is comment
    if "reply_to" in request.data:
        commented_post = get_object_or_404(Post, pk=request.data["reply_to"])
        commented_page = commented_post.page
        # you can create new comment for post only if
        # you are a follower of the commented post page
        if commented_page.followers.filter(pk=user.id).exists():
            my_page = get_object_or_404(Page, pk=page_id, is_blocked=False)
            post = Post.objects.create(
                page=my_page,
                content=content
            )
            post.reply_to = commented_post
            post.save()
            page = my_page
        else:
            return None, "Error. Cannot reply to non following page post."
    # in case new post is just new page post
    else:
        page = get_object_or_404(
            Page, pk=page_id, owner=user, is_blocked=False)
        post = Post.objects.create(
            page=page,
            content=content
        )

    # notifying followers
    for follower in page.followers.all():
        notify_follower_about_new_post.delay(page.name, post.content, follower.email)

    return post, ""


def update_post(request, pk):
    content = request.data["content"]

    user = request.user
    post = get_object_or_404(Post, pk=pk)
    page = post.page
    if page.owner != user or page.is_blocked:
        return "Undefined post (maybe page is blocked).", status.HTTP_404_NOT_FOUND

    post.content = content
    post.save()

    return "Updated", status.HTTP_200_OK


def delete_post(request, pk):
    user = request.user
    post = get_object_or_404(Post, pk=pk)
    page_id = post.page.id

    if user.role == User.Roles.ADMIN or user.role == User.Roles.ADMIN:
        for likes in list(post.likes.all()):
            publish(CommandTypes.UNDO_PAGE_LIKE, {"id": str(page_id)})
        post.delete()
    else:
        if post.page.owner != user:
            return "Error. Undefined post.", status.HTTP_404_NOT_FOUND
        for likes in list(post.likes.all()):
            publish(CommandTypes.UNDO_PAGE_LIKE, {"id": str(page_id)})
        post.delete()

    return "Deleted", status.HTTP_200_OK


def like_post(request, pk):
    user = request.user
    post = get_object_or_404(Post, pk=pk)

    if post.page.is_blocked:
        return "Error. Post page is blocked.", status.HTTP_400_BAD_REQUEST

    if post.likes.filter(pk=user.pk).exists():
        post.likes.remove(user)
        publish(CommandTypes.UNDO_PAGE_LIKE, {"id": str(post.page.id)})
        msg = "Unliked"
    else:
        post.likes.add(user)
        publish(CommandTypes.NEW_PAGE_LIKE, {"id": str(post.page.id)})
        msg = "Liked"
        
    return msg, status.HTTP_200_OK


def news_posts(request):
    user = request.user
    my_pages = user.pages.all()
    followed_pages = user.follows.all()
    posts = Post.objects.filter(Q(page__in=my_pages) | Q(page__in=followed_pages))
    return posts.values(), status.HTTP_200_OK