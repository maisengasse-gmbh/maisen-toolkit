from django.contrib.auth.models import Group
from django.test import TestCase

from maisen.toolkit.totp.models import GroupTotpRequirement
from maisen.toolkit.totp.utils import user_requires_totp


class UserRequiresTotpTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="admin", password="test"
        )
        cls.normal_user = User.objects.create_user(
            username="user", password="test"
        )
        cls.group = Group.objects.create(name="totp-required")
        GroupTotpRequirement.objects.create(group=cls.group, totp_required=True)

    def test_superuser_always_requires_totp(self):
        self.assertTrue(user_requires_totp(self.superuser))

    def test_normal_user_no_totp_required(self):
        self.assertFalse(user_requires_totp(self.normal_user))

    def test_user_in_totp_group_requires_totp(self):
        self.normal_user.groups.add(self.group)
        self.assertTrue(user_requires_totp(self.normal_user))
        self.normal_user.groups.remove(self.group)

    def test_group_totp_str(self):
        req = GroupTotpRequirement.objects.first()
        self.assertIn("erforderlich", str(req))
