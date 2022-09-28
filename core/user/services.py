from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime, timedelta
from user.models import User
from core.settings import AWS_CREDENTIALS as AWS, JWT_SECRET, JWT_ALGORITHM, JWT_ACCESS_TIME, JWT_REFRESH_TIME
from core.aws import s3

def register_user(request):
    username = request.data["username"]
    email = request.data["email"]
    password = request.data["password"]

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return {"user_id": user.id}, status.HTTP_200_OK


def block_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    new_status = not user.is_blocked
    user.is_blocked = new_status
    user.save()

    for page in user.pages.all():
        page.is_blocked = new_status
        page.save()

    return ("User unblocked." if not new_status else "User blocked."), status.HTTP_200_OK


def search_user(request):
    username = request.data["username"]
    title = request.data["title"]
    users = User.objects.filter(
        Q(username__contains=username) & Q(title__contains=title))

    return users.values(), status.HTTP_200_OK


def update_user_avatar(request, pk):
    IMAGE_EXTS = ("png", "jpg", "jpeg", "gif")
    user = request.user
    if int(user.pk) != int(pk):
        return {"Error": "Wrong user id."}, status.HTTP_400_BAD_REQUEST    

    file = request.FILES["img"]
    file_ext = file.name.split(".")[-1]
    if not file_ext in IMAGE_EXTS:
        return {"Error": f"Invalid file extension .{file_ext} ."}, status.HTTP_400_BAD_REQUEST 

    timestamp = int(datetime.now().timestamp())
    s3_key = f"{file.name}_{str(user.pk)}{str(timestamp)}"

    s3.put_object(
        Bucket=AWS["AWS_BUCKET_NAME"],
        Key=s3_key,
        Body=file
    )

    user.image_s3_key = s3_key
    user.save()

    exp_time = 60*60*24*7 # 1 week
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": AWS["AWS_BUCKET_NAME"],
            "Key": s3_key
        },
        ExpiresIn=exp_time
    )

    return {"avatar_url": url}, status.HTTP_200_OK


# _____JWT OUTDATED_____


# def login_user(request):
#     email = request.data["email"]
#     get_object_or_404(User, email=email)

#     return Response(
#         data={"logged": True},
#         status=status.HTTP_200_OK
#     )


# def gen_tokens_pair(user):
#     access = jwt.encode({
#         "id": user.id,
#         "email": user.email,
#         "exp": datetime.now() + timedelta(seconds=JWT_ACCESS_TIME)
#     }, JWT_SECRET, algorithm=JWT_ALGORITHM)

#     refresh = jwt.encode({
#         "id": user.id,
#         "exp": datetime.now() + timedelta(seconds=JWT_REFRESH_TIME)
#     }, JWT_SECRET, algorithm=JWT_ALGORITHM)

#     RefreshToken.objects.update_or_create(
#         owner=user,
#         defaults={"refresh_token": refresh, "owner": user}
#     )

#     return {
#         "access": access,
#         "refresh": refresh
#     }


# def login_user(request):
#     email = request.data["email"]
#     user = get_object_or_404(User, email=email)

#     return Response(
#         data=gen_tokens_pair(user),
#         status=status.HTTP_200_OK
#     )


# def register_user(request):
#     username = request.data["username"]
#     email = request.data["email"]
#     password = request.data["password"]

#     user = User.objects.create_user(
#         username=username,
#         email=email,
#         password=password
#     )

#     return Response(
#         data=gen_tokens_pair(user),
#         status=status.HTTP_200_OK
#     )


# def rotate_tokens(request):
#     refresh = request.data["refresh_token"]
#     try:
#         payload = jwt.decode(refresh, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         user = User.objects.get(pk=payload["id"])
#         RefreshToken.objects.get(owner=user, refresh_token=refresh)
#     except jwt.ExpiredSignatureError:
#         return Response(
#             data={"Error": "Refresh token expired."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )
#     except:
#         return Response(
#             data={"Error": "Invalid token."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     return Response(
#         data=gen_tokens_pair(user),
#         status=status.HTTP_200_OK
#     )
