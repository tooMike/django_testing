from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestAddForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Пользователь")
        cls.reader = User.objects.create(username="Читатель")
        cls.note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """Проверяем отображения заметок у автора и другого пользователя"""
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse("notes:list")
        for user, status in users_statuses:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context["object_list"]
            self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        """
        Проверяем отображение формы 
        на странице добавления и изменения заметки
        """
        urls = (("notes:edit", (self.note.slug,)), ("notes:add", None))
        for adress, args in urls:
            url = reverse(adress, args=args)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn("form", response.context)
            self.assertIsInstance(response.context["form"], NoteForm)
