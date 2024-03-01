import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.parametrize(
    "user, result",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("not_author_client"), True),
    ),
)
def test_pages_contains_form(db, user, result, comment_id_for_args):
    """Проверяем доступность формы для добавления комментария"""
    url = reverse("news:detail", args=comment_id_for_args)
    response = user.get(url)
    assert ("form" in response.context) is result
    if "form" in response.context:
        assert isinstance(response.context["form"], CommentForm)


@pytest.mark.django_db
@pytest.mark.usefixtures("create_11_news")
def test_news_count(client):
    """Проверяем что на главной отображается 10 публикаций"""
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures("create_11_news")
def test_news_order(client):
    """Проверяем, что новости отсортированы от новых к старым"""
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures("create_10_comments")
def test_comments_order(client, news_id_for_args):
    """Проверяем, что комментарии отсортированы от старых к новым"""
    url = reverse("news:detail", args=news_id_for_args)
    response = client.get(url)
    news = response.context["news"]
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
