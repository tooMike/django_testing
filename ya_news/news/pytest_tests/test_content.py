import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.parametrize(
    "client_, expected_result",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("not_author_client"), True),
    ),
)
def test_pages_contains_form(
        client_,
        expected_result,
        news_detail_url,
    ):
    """Проверяем доступность формы для добавления комментария"""
    response = client_.get(news_detail_url)
    assert (
        isinstance(response.context.get("form"), CommentForm)
        is expected_result
    )


@pytest.mark.usefixtures("create_several_news")
def test_news_count(client, home_url):
    """Проверяем что на главной отображается 10 публикаций"""
    response = client.get(home_url)
    assert "object_list" in response.context
    object_list = response.context["object_list"]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures("create_several_news")
def test_news_order(client, home_url):
    """Проверяем, что новости отсортированы от новых к старым"""
    response = client.get(home_url)
    assert "object_list" in response.context
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures("create_10_comments")
def test_comments_order(client, news_detail_url):
    """Проверяем, что комментарии отсортированы от старых к новым"""
    response = client.get(news_detail_url)
    assert "news" in response.context
    news = response.context["news"]
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
