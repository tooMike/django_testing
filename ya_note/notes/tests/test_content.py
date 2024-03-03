from django.contrib.auth import get_user_model
from django.test import Client

from notes.forms import NoteForm
from .base_test import BaseTest


User = get_user_model()


class TestAddForm(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_notes_list_for_different_users(self):
        """Проверяем отображения заметок у автора и другого пользователя"""
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user_client, status in users_statuses:
            response = user_client.get(self.NOTE_LIST_URL)
            object_list = response.context["object_list"]
            self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        """
        Проверяем отображение формы
        на странице добавления и изменения заметки
        """
        urls = (self.NOTE_EDIT_URL, self.NOTE_ADD_URL)
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn("form", response.context)
            self.assertIsInstance(response.context["form"], NoteForm)
