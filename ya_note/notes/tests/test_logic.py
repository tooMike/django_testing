from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.note_form_data = {
            "title": "Title1", "text": "Text1", "slug": "slug1"
        }
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.success_url = reverse("notes:success")

    def test_anonymous_user_cant_create_note(self):
        """Поверяем, может ли анонимный пользователь создать заметку"""
        url = reverse("notes:add")
        response = self.client.post(url, data=self.note_form_data)
        login_url = reverse("users:login")
        expected_url = f"{login_url}?next={url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Поверяем, может ли залогиненный пользователь создать заметку"""
        url = reverse("notes:add")
        response = self.author_client.post(url, data=self.note_form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note_form_data["title"])
        self.assertEqual(new_note.text, self.note_form_data["text"])
        self.assertEqual(new_note.slug, self.note_form_data["slug"])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        """Проверяем, что невозможно создать две заметки с одинаковым slug"""
        self.note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=self.author
        )
        url = reverse("notes:add")
        self.note_form_data["slug"] = self.note.slug
        response = self.author_client.post(url, data=self.note_form_data)
        self.assertFormError(
            response,
            form="form",
            field="slug",
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """
        Проверяем, что если при создании заметки не заполнен slug,
        то он формируется автоматически
        """
        url = reverse("notes:add")
        self.note_form_data.pop("slug")
        response = self.author_client.post(url, data=self.note_form_data)
        self.assertRedirects(response, self.success_url)
        expected_slug = slugify(self.note_form_data["title"])
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяем что автор может редактировать свою заметку"""
        note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=self.author
        )
        url = reverse("notes:edit", args=(note.slug,))
        response = self.author_client.post(url, data=self.note_form_data)
        self.assertRedirects(response, self.success_url)
        note.refresh_from_db()
        self.assertEqual(note.title, self.note_form_data["title"])
        self.assertEqual(note.text, self.note_form_data["text"])
        self.assertEqual(note.slug, self.note_form_data["slug"])

    def test_other_user_cant_edit_note(self):
        """
        Проверяем что зарегистрированный пользователь
        не может редактировать чужую заметку
        """
        note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=self.author
        )
        url = reverse("notes:edit", args=(note.slug,))
        response = self.reader_client.post(url, data=self.note_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверяем что автор может удалять свои заметки"""
        note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=self.author
        )
        url = reverse("notes:delete", args=(note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Проверяем что не автор не может удалять чужие заметки"""
        note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=self.author
        )
        url = reverse("notes:delete", args=(note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
