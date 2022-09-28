from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include("user.urls")),
    path('api/app/', include("page.urls"))
]

