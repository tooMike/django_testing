from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .base_test import BaseTest


User = get_user_model()


class TestLogic(BaseTest):

    def check_note(self):
        """Проверяем соответсвуют ли параметры заметки ожидаемым значениям"""
        self.assertEqual(self.note.title, self.note_form_data["title"])
        self.assertEqual(self.note.text, self.note_form_data["text"])
        self.assertEqual(self.note.slug, self.note_form_data["slug"])

    def test_anonymous_user_cant_create_note(self):
        """
        Проверяем, что незарегистрированный пользователь
        не может создавать заметку
        """
        # Получаем количество заметок до начала теста
        notes_count = Note.objects.count()
        response = self.client.post(
            self.NOTE_ADD_URL,
            data=self.note_form_data
        )
        expected_url = f"{self.LOGIN_URL}?next={self.NOTE_ADD_URL}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_create_note(self):
        """Поверяем, что залогиненный пользователь может создать заметку"""
        # Удаляем все объекты заметок из БД
        Note.objects.all().delete()
        response = self.author_client.post(
            self.NOTE_ADD_URL,
            data=self.note_form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.author, self.author)
        self.check_note()

    def test_not_unique_slug(self):
        """Проверяем, что невозможно создать две заметки с одинаковым slug"""
        notes_count = Note.objects.count()
        self.note_form_data["slug"] = self.note.slug
        response = self.author_client.post(
            self.NOTE_ADD_URL,
            data=self.note_form_data
        )
        self.assertFormError(
            response,
            form="form",
            field="slug",
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        """
        Проверяем, что если при создании заметки не заполнен slug,
        то он формируется автоматически
        """
        # Удаляем все объекты заметок из БД
        Note.objects.all().delete()
        self.note_form_data.pop("slug")
        response = self.author_client.post(
            self.NOTE_ADD_URL,
            data=self.note_form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        expected_slug = slugify(self.note_form_data["title"])
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяем что автор может редактировать свою заметку"""
        response = self.author_client.post(
            self.NOTE_EDIT_URL,
            data=self.note_form_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.check_note()

    def test_other_user_cant_edit_note(self):
        """
        Проверяем что зарегистрированный пользователь
        не может редактировать чужую заметку
        """
        response = self.reader_client.post(
            self.NOTE_EDIT_URL,
            data=self.note_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверяем что автор может удалять свои заметки"""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.NOTE_DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        """Проверяем что не автор не может удалять чужие заметки"""
        notes_count = Note.objects.count()
        response = self.reader_client.post(self.NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
