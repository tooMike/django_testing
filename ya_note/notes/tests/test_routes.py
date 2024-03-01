from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.note = Note.objects.create(
            title="Title1", text="Text1", slug="slug1", author=cls.author
        )

    def test_pages_availability_for_auth_user(self):
        """Проверяем доступность страниц авторизированным пользователям"""
        urls = (("notes:list"), ("notes:add"), ("notes:success"))
        self.client.force_login(self.reader)
        for adress in urls:
            with self.subTest(name=adress):
                url = reverse(adress)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """Проверяем доступность удаления и редактирования комментариев"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
            ("notes:detail", (self.note.slug,)),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for adress, args in urls:
                with self.subTest(name=user):
                    url = reverse(adress, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        """Проверяем доступность страниц для всех пользователей"""
        urls = (
            ("notes:home", None),
            ("users:login", None),
            ("users:logout", None),
            ("users:signup", None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверяем редиректы"""
        login_url = reverse("users:login")

        urls = (
            ("notes:detail", (self.note.slug,)),
            ("notes:list", None),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
            ("notes:add", None),
            ("notes:success", None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
