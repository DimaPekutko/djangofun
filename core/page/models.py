from django.db import models


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField("Tag", blank=True, related_name='pages')

    owner = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField(
        "user.User", blank=True, related_name='follows')

    image = models.URLField(null=True, blank=True)

    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField(
        "user.User", blank=True, related_name='requests')

    unblock_date = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=180)

    reply_to = models.ForeignKey(
        "Post", blank=True, on_delete=models.SET_NULL, null=True, related_name='replies')

    likes = models.ManyToManyField(
        "user.User", default=[], blank=True, editable=False, related_name='likes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content