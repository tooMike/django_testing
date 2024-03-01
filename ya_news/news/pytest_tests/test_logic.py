from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_author_can_delete_comment(
    author_client, comment_id_for_args, news_id_for_args
):
    """Проверяем, что автор может удалить свой комментарий"""
    url = reverse("news:delete", args=comment_id_for_args)
    url_to_comments = (
        reverse("news:detail", args=news_id_for_args) + "#comments"
    )
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_id_for_args
):
    """Проверяем, что пользователь не может удалить чужой комментарий"""
    url = reverse("news:delete", args=comment_id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_can_edit_comment(
    author_client,
    comment_id_for_args,
    comment, news_id_for_args,
    comment_form_data
):
    """Проверяем, что автор может изменять свои комментарии"""
    url = reverse("news:edit", args=comment_id_for_args)
    url_to_comments = (
        reverse("news:detail", args=news_id_for_args) + "#comments"
    )
    response = author_client.post(url, comment_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_form_data["text"]


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, comment_id_for_args, comment_form_data
):
    """Проверяем, что пользователь не может изменять чужие комментарии"""
    url = reverse("news:edit", args=comment_id_for_args)
    response = not_author_client.post(url, comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_id_for_args, comment_form_data
):
    """Проверяем, что анонимный пользователь не может добавлять комментарии"""
    url = reverse("news:detail", args=news_id_for_args)
    client.post(url, comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    not_author_client, news_id_for_args, comment_form_data
):
    """Проверяем, что пользователь может добавлять комментарии"""
    url = reverse("news:detail", args=news_id_for_args)
    response = not_author_client.post(url, comment_form_data)
    assertRedirects(response, f"{url}#comments")
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form_data["text"]


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_id_for_args, not_author_client):
    """Проверяем, что в комментарии нельзя использовать некоторые слова"""
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    url = reverse("news:detail", args=news_id_for_args)
    response = not_author_client.post(url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)
    assert Comment.objects.count() == 0
