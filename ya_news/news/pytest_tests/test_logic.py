from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


def test_author_can_delete_comment(
        author_client,
        comment_delete_url,
        news_detail_url,
):
    """Проверяем, что автор может удалить свой комментарий"""
    url_to_comments = news_detail_url + "#comments"
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_delete_url
):
    """Проверяем, что пользователь не может удалить чужой комментарий"""
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        comment_edit_url,
        comment_form_data,
        news_detail_url,
):
    """Проверяем, что автор может изменять свои комментарии"""
    url_to_comments = news_detail_url + "#comments"
    response = author_client.post(comment_edit_url, comment_form_data)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_form_data["text"] == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment,
        comment_edit_url,
        comment_form_data,
):
    """Проверяем, что пользователь не может изменять чужие комментарии"""
    response = not_author_client.post(comment_edit_url, comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_anonymous_user_cant_create_comment(
        client, comment_form_data, news_detail_url
):
    """Проверяем, что анонимный пользователь не может добавлять комментарии"""
    client.post(news_detail_url, comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        not_author,
        comment_form_data,
        not_author_client,
        news,
        news_detail_url,
):
    """Проверяем, что пользователь может добавлять комментарии"""
    response = not_author_client.post(news_detail_url, comment_form_data)
    assertRedirects(response, f"{news_detail_url}#comments")
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form_data["text"]
    assert new_comment.author == not_author
    assert new_comment.news == news


def test_user_cant_use_bad_words(
        bad_words_data,
        not_author_client,
        news_detail_url,
):
    """Проверяем, что в комментарии нельзя использовать некоторые слова"""
    response = not_author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)
    assert Comment.objects.count() == 0
