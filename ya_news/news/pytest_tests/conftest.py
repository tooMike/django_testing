from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title="Заголовок",
        text="Текст",
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def create_several_news():
    today = datetime.today()
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text="Текст комментария",
    )


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def comment_form_data(news, author):
    return {
        "text": "Новый текст комментария",
    }


@pytest.fixture
def create_10_comments(news, author):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Tекст {index}",
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def bad_words_data():
    return {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}


@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def news_detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse("news:delete", args=(comment.id,))


@pytest.fixture
def comment_edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse("users:login")


@pytest.fixture
def logout_url():
    return reverse("users:logout")


@pytest.fixture
def signup_url():
    return reverse("users:signup")
