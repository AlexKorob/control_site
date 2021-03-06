import json
from django.test import TestCase
from django.shortcuts import reverse
from django.test import Client
from .models import User


class UserCreateTestCase(TestCase):
    fixtures = ["ads.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('user_create')
        cls.parameters = {'username': 'oleg', 'password': '123sS123',
                          'phone': '+30774562664', 'email': 'oleg@gmail.com'}

    def test_create_user(self):
        users_on_db_count = User.objects.count()
        client = self.client.post(self.url, self.parameters)
        self.assertEqual(client.status_code, 201)
        self.assertEqual(User.objects.count(), users_on_db_count + 1)
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
        parameters["password"] = "123sS123"
        parameters["email"] = "masha@gmail.com"
        self.assertEqual(client.status_code, 400)


class UserAuthorizationTestCase(TestCase):
    fixtures = ["ads.json"]

    def test_user_authorization(self):
        url = reverse('user_auth')
        parameters = {'username': 'alexandr', 'password': '1234567dD'}
        client = self.client.post(url, parameters)
        self.assertEqual(client.status_code, 200)
        self.assertTrue(client.data.get("token"))

    def test_user_authorization_fail(self):
        url = reverse('user_auth')
        parameters = {'username': 'oleg', 'password': '1123'}
        client = self.client.post(url, parameters)
        self.assertEqual(client.status_code, 400)


class AdTestCase(TestCase):
    fixtures = ["ads.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("ads-list")
        self.username = "alexandr"
        self.password = "1234567dD"
        self.client.login(username=self.username, password=self.password)
        self.ad_id = self.client.post(reverse("ads-list"), {"title": "Sold Refrigerator",
                                                            "category": "Холодильники",
                                                            "description": "???"}).data["id"]

    def test_create_ad(self):
        parameters = {"title": "Sold", "category": "Холодильники", "description": "..."}
        response = self.client.post(self.url, parameters)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["creator"], self.username)

        # This needed for deleting test img from hard disk
        ad_id = str(response.data["id"])
        self.client.delete(self.url + ad_id + "/")

    def test_create_ad_not_authorization_fail(self):
        client = Client()
        parameters = {"title": "Sold", "category": "Холодильники", "description": "..."}
        response = client.post(self.url, parameters)
        self.assertTrue(response.data["detail"].startswith("Authentication credentials were not"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.status_text, "Unauthorized")

    def test_add_images_to_ad(self):
        url = reverse("images-list")
        ad_id = str(self.ad_id)
        with open("media/ad_images/6314045_0.jpg", "rb") as img_1, \
             open("media/ad_images/image.webp", "rb") as img_2:

             img_1_id = self.client.post(url, {"image": img_1, "ad": ad_id}).data["id"]
             img_2_id = self.client.post(url, {"image": img_2, "ad": ad_id}).data["id"]

        response = self.client.get(url + ad_id + "/")

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.status_code, 200)

        self.client.delete(url + str(img_1_id) + "/")
        self.client.delete(url + str(img_2_id) + "/")

    def test_add_image_to_ad_fail(self):
        client = Client()
        url = reverse("images-list")
        ad_id = str(self.ad_id)
        with open("media/ad_images/6314045_0.jpg", "rb") as img:
            response = client.post(url, {"image": img, "ad": ad_id})
            self.assertEqual(response.status_code, 401)

    def test_partial_update_own_ad(self):
        url = self.url + str(self.ad_id) + "/"
        data = json.dumps({"title": "Sold cycle", "price": "8000", "contractual": "true",
                           "status": "20", "category": "Велосипеды"})
        response = self.client.patch(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["description"], "???")

    def test_partial_update_pesmission_denied(self):
        url = self.url + "1/"
        data = json.dumps({"title": "Sold cycle"})
        response = self.client.patch(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data["detail"].startswith("You do not have permission "))

    def test_update_own_ad(self):
        url = self.url + str(self.ad_id) + "/"
        data = json.dumps({"title": "Sold cycle", "contractual": "true",
                           "category": "Велосипеды", "description": "..."})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data["price"]), 0.00)

    def test_update_permission_denied(self):
        url = self.url + "1/"
        data = json.dumps({"title": "Sold cycle"})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data["detail"].startswith("You do not have permission "))

    def test_delete_own_ad(self):
        url = self.url + str(self.ad_id) + "/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_pesmission_denied(self):
        url = self.url + "1/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data["detail"].startswith("You do not have permission "))

    def test_get_all_ads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.status_text, "OK")

    def test_get_one_ad(self):
        url = self.url + "2/"
        response = self.client.get(url)
        self.assertEqual(response.status_text, "OK")
        self.assertTrue(isinstance(response.data, dict))
        self.assertEqual(response.data["id"], 2)
