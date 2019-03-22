from django.test import TestCase
from django.shortcuts import reverse
from .models import User


class UserCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('user_create')
        cls.parameters = {'username': 'oleg', 'password': '123sS123',
                      'phone': '+30774562664', 'email': 'oleg@gmail.com'}

    def test_create_user(self):
        client = self.client.post(self.url, self.parameters)
        self.assertEqual(client.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(client.data.startswith("Token "))

    def test_create_user_fail(self):
        parameters = self.parameters
        self.client.post(self.url, parameters)
        client = self.client.post(self.url, parameters)
        self.assertEqual(client.status_code, 400)
        parameters["username"] = "masha"
        self.assertEqual(client.status_code, 400)
        parameters["phone"] = "+30774562666"
        self.assertEqual(client.status_code, 400)
        parameters["email"] = ""
        self.assertEqual(client.status_code, 400)
        parameters["password"]= "123sS123"
        parameters["email"] = "masha@gmail.com"
        self.assertEqual(client.status_code, 400)


class UserAuthorizationTestCase(TestCase):
    fixtures = ["user.json"]

    def test_user_authorization(self):
        url = reverse('user_auth')
        parameters = {'username': 'oleg', 'password': '123sS123'}
        client = self.client.post(url, parameters)
        self.assertEqual(client.status_code, 200)
        self.assertTrue(client.data.startswith("Token "))

    def test_user_authorization_fail(self):
        url = reverse('user_auth')
        parameters = {'username': 'oleg', 'password': '123'}
        client = self.client.post(url, parameters)
        self.assertEqual(client.status_code, 400)
