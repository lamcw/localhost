from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

USER_CREDENTIALS = {'email': 'testuser@testbase.com', 'password': '1234'}


class SignUpViewTest(TestCase):
    pass


class LoginViewTest(TestCase):
    """
    Test if user is able to log in with email and password only.
    """

    @classmethod
    def setUpTestData(cls):
        cls.credentials = USER_CREDENTIALS
        User.objects.create_user(**cls.credentials)

    def test_login(self):
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('authentication:login'), self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
