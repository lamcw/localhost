from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase

User = get_user_model()


class SettingsTest(TestCase):
    def test_is_configured(self):
        self.assertTrue('authentication.User' == settings.AUTH_USER_MODEL)


class UserTest(TestCase):
    def setUp(self):
        self.email = "testuser@testbase.com"
        self.first_name = "Test"
        self.last_name = "User"
        self.password = "z"
        self.dob = '1990-01-01'
        self.gender = 'M'

        self.test_user = User.objects.create_user(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            dob=self.dob,
            gender=self.gender,
        )

    def test_create_user(self):
        self.assertIsInstance(self.test_user, User)

    def test_default_user_is_active(self):
        self.assertTrue(self.test_user.is_active)

    def test_default_user_is_staff(self):
        self.assertFalse(self.test_user.is_staff)

    def test_default_user_is_superuser(self):
        self.assertFalse(self.test_user.is_superuser)

    def test_get_full_name(self):
        self.assertEqual('Test User', self.test_user.get_full_name())

    def test_str(self):
        self.assertEqual(self.email, self.test_user.__str__())

    def test_invalid(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                first_name=self.first_name,
                last_name=self.last_name,
                dob=self.dob,
                gender=self.gender)
