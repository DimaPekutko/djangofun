import pytest
from unittest import mock
import json
from user.models import User
from user.views import RegisterViewSet
from page.views.page_view import PageViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from django.core.management import call_command

req_factory = APIRequestFactory()

@pytest.fixture(scope='session')
def db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'user/fixtures/users.json')


@pytest.mark.django_db
@mock.patch("core.producer.publish", return_value=None)
def test_create_page(publish):
    payload = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "secret_pass"
    }
    request = req_factory.post("/users/register/", data=json.dumps(payload), content_type="application/json")
    response = RegisterViewSet.as_view({"post": "create"})(request)

    user = User.objects.get(pk=response.data["user_id"])

    payload2 = {
        "name": "name",
        "uuid": "dkaepodjei",
        "description": "desc"
    }

    request2 = req_factory.post("/api/app/pages/", data=json.dumps(payload2), content_type="application/json")
    force_authenticate(request2, user)
    response2 = PageViewSet.as_view({"post": "create"})(request2)

    assert response2.status_code == 200