from django.test import TestCase

from maisen.toolkit.totp.forms import TotpCodeForm


class TotpCodeFormTest(TestCase):
    def test_valid_code(self):
        form = TotpCodeForm(data={"code": "123456"})
        self.assertTrue(form.is_valid())

    def test_too_short(self):
        form = TotpCodeForm(data={"code": "12345"})
        self.assertFalse(form.is_valid())

    def test_too_long(self):
        form = TotpCodeForm(data={"code": "1234567"})
        self.assertFalse(form.is_valid())

    def test_empty(self):
        form = TotpCodeForm(data={"code": ""})
        self.assertFalse(form.is_valid())

    def test_widget_attrs(self):
        form = TotpCodeForm()
        widget = form.fields["code"].widget
        self.assertEqual(widget.attrs["inputmode"], "numeric")
        self.assertEqual(widget.attrs["autocomplete"], "one-time-code")
