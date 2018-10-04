from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase

User = get_user_model()


class SettingsTest(TestCase):
    def test_is_configured(self):
        self.assertTrue('authentication.User' == settings.AUTH_USER_MODEL)


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = 'testuser@testbase.com'
        cls.first_name = 'Test'
        cls.last_name = 'User'
        cls.password = 'z'
        cls.dob = '1990-01-01'
        cls.gender = 'M'

        cls.test_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            last_name=cls.last_name,
            dob=cls.dob,
            gender=cls.gender,
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
        self.assertEqual('Test User', self.test_user.full_name)

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
