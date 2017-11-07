from django.test import TestCase, Client
from django.conf import settings


class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client = None

    def test_login_view(self):
        """
        Test the login view loads when we're an anonymous user.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_authenticate_view(self):
        """
        Test the authenticate view renders correctly with a shop param.
        """
        response = self.client.get('/authenticate/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/authenticate/', follow=True)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/authenticate/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/?shop=test.myshopify.com')
        self.assertContains(response, 'window.top.location.href = "https://test.myshopify.com/admin/oauth/authorize')

        # Dev mode so token does not need to be valid
        settings.SHOPIFY_APP_DEV_MODE = True
        response = self.client.get('/authenticate/?shop=test.myshopify.com')
        self.assertEqual(response.status_code, 200)

