from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    "name, args",
    (
        ("news:home", None),
        ("news:detail", pytest.lazy_fixture("news_id_for_args")),
        ("users:login", None),
        ("users:logout", None),
        ("users:signup", None),
    ),
)
def test_pages_availability_for_anonymous_user(db, client, name, args):
    """Проверяем доступность старниц для анонимных пользователй"""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_response",
    (
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_response, name, args
):
    """Тестируем возможность удалять и изменять комментарии"""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_response


@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_redirect_for_anonymous_client(db, client, name, args):
    """Тестируем редиректы"""
    login_url = reverse("users:login")
    url = reverse(name, args=args)
    redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, redirect_url)
