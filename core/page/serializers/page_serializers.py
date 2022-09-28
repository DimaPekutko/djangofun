from rest_framework.serializers import UUIDField, CharField, BooleanField, ModelSerializer, DateTimeField, PrimaryKeyRelatedField, Serializer
from rest_framework.response import Response
from user.serializers import UserSerializer
from page.models import Page, Post, Tag
from user.models import User
from core.producer import publish, CommandTypes


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class PageSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    followers = UserSerializer(many=True)
    follow_requests = UserSerializer(many=True)

    class Meta:
        model = Page
        fields = ("id", "owner", "uuid", "name", "follow_requests", "description", "followers", "is_blocked", "is_private", "tags")


class CreatePageSerializer(ModelSerializer):
    class Meta:
        model = Page
        exclude = ("follow_requests", "followers", "tags", "owner")

    def create(self, validated_data):
        user =  self.context['request'].user
        page = Page.objects.create(
            name=validated_data["name"],
            uuid=validated_data["uuid"],
            description=validated_data["description"],
            owner=user
        )
        publish(CommandTypes.CREATE_PAGE, {
            "name": page.name,
            "id": str(page.id),
            "user_id": str(user.id)
        })
        return page


class UpdatePageSerializer(ModelSerializer):
    class Meta:
        model = Page
        fields = ("uuid", "name", "description")

    def update(self, inst, validated_data):
        Page.objects.filter(pk=inst.pk, is_blocked=False).update(
            name = validated_data["name"],
            description = validated_data["description"],
            uuid = validated_data["uuid"]
            
        )
        publish(CommandTypes.UPDATE_PAGE, {
            "name": validated_data["name"],
            "id": str(inst.id),
            "user_id": str(inst.owner.id)
        })
        return inst

class PageRequestActionSerializer(Serializer):
    id = PrimaryKeyRelatedField(queryset=User.objects.all())
    to_approve = BooleanField()

    # class Meta():
    #     model = User
    #     fields = ("id", "to_approve")


class PageAllRequestsActionSerializer(Serializer):
    to_approve = BooleanField()


class PageBlockSerializer(ModelSerializer):
    unblock_date = DateTimeField(required=True, allow_null=True)

    class Meta:
        model = Page
        fields = ("unblock_date",)

class PageSearchSerializer(ModelSerializer):
    tag_name = CharField(allow_blank=True)
    class Meta:
        model = Page
        fields = ("name", "uuid", "tag_name")

# class PageSerializer(ModelSerializer):
#     tags = TagSerializer(many=True)
#     followers = UserSerializer(many=True)
#     follow_requests = UserSerializer(many=True)

#     class Meta:
#         model = Page
#         fields = "__all__"