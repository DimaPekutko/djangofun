from rest_framework.routers import DefaultRouter
# from page.views import PageViewSet, PostViewSet, TagViewSet

from page.views.page_view import PageViewSet
from page.views.post_view import PostViewSet

router = DefaultRouter()
router.register(r"pages", PageViewSet)
router.register(r"posts", PostViewSet)

urlpatterns = router.urls