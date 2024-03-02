from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


HOME_URL = pytest.lazy_fixture("home_url")
NEWS_DETAIL_URL = pytest.lazy_fixture("news_detail_url")
COMMENT_EDIT_URL = pytest.lazy_fixture("comment_edit_url")
COMMENT_DELETE_URL = pytest.lazy_fixture("comment_delete_url")
LOGIN_URL = pytest.lazy_fixture("login_url")
LOGOUT_URL = pytest.lazy_fixture("logout_url")
SIGNUP_URL = pytest.lazy_fixture("signup_url")


@pytest.mark.parametrize(
    "url",
    (
        HOME_URL,
        NEWS_DETAIL_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGNUP_URL,
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """Проверяем доступность старниц для анонимных пользователй"""
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
    "url",
    (
        COMMENT_EDIT_URL,
        COMMENT_DELETE_URL,
    ),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_response, url
):
    """Тестируем возможность удалять и изменять комментарии"""
    response = parametrized_client.get(url)
    assert response.status_code == expected_response


@pytest.mark.parametrize(
    "url",
    (
        COMMENT_EDIT_URL,
        COMMENT_DELETE_URL,
    ),
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """Тестируем редиректы"""
    redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, redirect_url)
