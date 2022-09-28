from dataclasses import field
from django.forms import CharField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from user.models import User
from django.contrib.auth.hashers import check_password

from core.aws import s3
from core.settings import AWS_CREDENTIALS as AWS


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField("get_avatar_url")

    class Meta:
        model = User
        fields = ("id", "email", "avatar_url",
                  "role", "title", "is_blocked")

    def get_avatar_url(self, obj):
        s3_key = obj["image_s3_key"]
        exp_time = 60*60*24*7  # 1 week
        if s3_key is None:
            return ""
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": AWS["AWS_BUCKET_NAME"],
                "Key": s3_key
            },
            ExpiresIn=exp_time
        )
        return url


class UserBlockSerializer(serializers.ModelSerializer):
    unblock_date = serializers.DateTimeField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ("unblock_date",)


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("title", "username")
        extra_kwargs = {
            "title": {
                "allow_blank": True
            },
            "username": {
                "allow_blank": True,
                "validators": []
            }
        }


class UserUpdateAvatarSerializer(serializers.Serializer):
    img = serializers.FileField()


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")


#  ____JWT OTDATED___

# class LoginUserSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=False)

#     class Meta:
#         model = User
#         fields = ("email", "password")

#     def validate(self, data):
#         email = data["email"]
#         password = data["password"]
#         user = get_object_or_404(User, email=email)
#         if not check_password(password, user.password):
#             raise serializers.ValidationError("Invalid credentionals.")
#         return data

# class RefreshTokenSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RefreshToken
#         fields = ("refresh_token",)
