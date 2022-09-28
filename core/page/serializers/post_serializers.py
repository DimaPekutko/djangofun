from rest_framework import serializers
from page.models import Post
from page.services import post_service

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "created_at", "updated_at", "page", "reply_to", "likes")
        read_only_fields = ("page",)

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("page", "content", "reply_to")

    def create(self, validated_data):
        inst, err = post_service.create_post(self.context['request'])
        if not inst:
            raise serializers.ValidationError(err)
        return inst

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("content",)

    def update(self, inst, validated_data):
        Post.objects.filter(pk=inst.pk).update(
            content=validated_data["content"]
        )
        return inst
