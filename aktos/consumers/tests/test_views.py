import unittest

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from aktos.users.models import User


@pytest.mark.django_db
class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="fake@test.com", password="password")
        self.client.force_authenticate(user=self.user)

    def test_consumer_list_api(self):
        # try it without model
        response = self.client.get(reverse("api:consumers:list") + "?page_size=10")
        assert response.status_code == 200, response.content
        data = response.json()
        assert 'results' in data


if __name__ == '__main__':
    unittest.main()
