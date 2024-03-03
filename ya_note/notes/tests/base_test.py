from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTest(TestCase):
    """Базовый класс фикстур"""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Пользователь")
        cls.reader = User.objects.create(username="Читатель")
        cls.note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=cls.author
        )
        cls.HOME_URL = reverse("notes:home")
        cls.NOTE_LIST_URL = reverse("notes:list")
        cls.NOTE_ADD_URL = reverse("notes:add")
        cls.NOTE_EDIT_URL = reverse("notes:edit", args=(cls.note.slug,))
        cls.SUCCESS_URL = reverse("notes:success")
        cls.NOTE_DELETE_URL = reverse("notes:delete", args=(cls.note.slug,))
        cls.NOTE_DETAIL_URL = reverse("notes:detail", args=(cls.note.slug,))
        cls.LOGIN_URL = reverse("users:login")
        cls.LOGOUT_URL = reverse("users:logout")
        cls.SIGNUP_URL = reverse("users:signup")
