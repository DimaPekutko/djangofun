import jwt
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from user.models import User
from core.settings import JWT_SECRET, JWT_ALGORITHM


class AuthMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        access_token = request.headers.get("authorization", None)
        if access_token is not None:
            try:
                payload = jwt.decode(
                    access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # in case of any decode error, there will be anon user
            except:
                return

            if "id" in payload and User.objects.filter(pk=payload["id"]).exists():
                request.user = User.objects.get(pk=payload["id"])