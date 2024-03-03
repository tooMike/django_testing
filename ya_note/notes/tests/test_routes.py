from http import HTTPStatus

from django.contrib.auth import get_user_model

from .base_test import BaseTest


User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability_for_auth_user(self):
        """
        Проверяем, что авторизированным пользователям доступны страницы
        со списком заметок, добавлением заметок и страница успешного добавления
        """
        urls = (self.NOTE_LIST_URL, self.NOTE_ADD_URL, self.SUCCESS_URL)
        self.client.force_login(self.reader)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """Проверяем доступность удаления и редактирования комментариев"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            self.NOTE_EDIT_URL,
            self.NOTE_DELETE_URL,
            self.NOTE_DETAIL_URL,
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(name=user):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        """Проверяем доступность страниц для всех пользователей"""
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверяем редиректы"""
        urls = (
            self.NOTE_DETAIL_URL,
            self.NOTE_LIST_URL,
            self.NOTE_EDIT_URL,
            self.NOTE_DELETE_URL,
            self.NOTE_ADD_URL,
            self.SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f"{self.LOGIN_URL}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
