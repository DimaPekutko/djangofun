import pytest
import json
from user.models import User
from user import views
from rest_framework.test import APIRequestFactory, force_authenticate
from django.core.management import call_command

req_factory = APIRequestFactory()


@pytest.fixture(scope='session')
def db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'user/fixtures/users.json')

@pytest.mark.django_db
def test_register(db_setup):
    payload = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "secret_pass"
    }
    request = req_factory.post("/users/register/", data=json.dumps(payload), content_type="application/json")
    response = views.RegisterViewSet.as_view({"post": "create"})(request)

    user_created = User.objects.filter(
        username=payload["username"]
    ).exists()

    assert response.status_code == 200
    assert user_created

@pytest.mark.django_db
def test_block_user(db_setup):
    admin = User.objects.get(pk=1)
    block_user_id = 3

    request = req_factory.put(f"/users/{block_user_id}/block/", content_type="application/json")
    force_authenticate(request, user=admin)
    response = views.UserViewSet.as_view({"put": "block"})(request, block_user_id)

    assert response.status_code == 200


@pytest.mark.django_db
def test_search_user(db_setup):
    user = User.objects.get(pk=1)

    payload = {
        "title": "",
        "username": user.username 
    }

    request = req_factory.post(f"/users/search/", data=json.dumps(payload), content_type="application/json")
    response = views.UserViewSet.as_view({"post": "search"})(request)


    assert response.status_code == 200
    assert response.data[0]["id"] == 1