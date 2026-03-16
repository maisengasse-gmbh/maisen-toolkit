from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from maisen.toolkit.totp.middleware import TotpMiddleware

User = get_user_model()


def dummy_response(request):
    from django.http import HttpResponse

    return HttpResponse("OK")


class TotpMiddlewareTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="admin", password="test"
        )
        cls.normal_user = User.objects.create_user(
            username="user", password="test"
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TotpMiddleware(dummy_response)

    def _make_request(self, path, user, session=None):
        request = self.factory.get(path)
        request.user = user
        request.session = session or {}
        return request

    def test_anonymous_user_passes_through(self):
        from django.contrib.auth.models import AnonymousUser

        request = self._make_request("/admin/", AnonymousUser())
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_normal_user_no_totp_required_passes(self):
        request = self._make_request("/admin/dashboard/", self.normal_user)
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_superuser_without_totp_redirects_to_setup(self):
        self.superuser.totp_enabled = False
        self.superuser.totp_secret = ""
        request = self._make_request("/admin/dashboard/", self.superuser)
        response = self.middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/totp/setup/", response.url)

    def test_superuser_with_totp_enabled_redirects_to_verify(self):
        self.superuser.totp_secret = "TESTSECRET123456"
        self.superuser.totp_enabled = True
        self.superuser.save()
        request = self._make_request("/admin/dashboard/", self.superuser)
        response = self.middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/totp/verify/", response.url)
        # Cleanup
        self.superuser.totp_secret = ""
        self.superuser.totp_enabled = False
        self.superuser.save()

    def test_totp_urls_are_exempt(self):
        request = self._make_request("/admin/totp/verify/", self.superuser)
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_verified_session_passes_through(self):
        self.superuser.totp_secret = "TESTSECRET123456"
        self.superuser.totp_enabled = True
        self.superuser.save()
        request = self._make_request(
            "/admin/dashboard/", self.superuser, session={"totp_verified": True}
        )
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        # Cleanup
        self.superuser.totp_secret = ""
        self.superuser.totp_enabled = False
        self.superuser.save()
