from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfileMixin(models.Model):
    """Abstract Mixin fuer gemeinsame User-Profil-Felder."""

    class Meta:
        abstract = True

    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_DIVERSE = 3
    GENDER_CHOICES = [
        (GENDER_MALE, _("Männlich")),
        (GENDER_FEMALE, _("Weiblich")),
        (GENDER_DIVERSE, _("Divers")),
    ]

    phone = models.CharField(
        _("Telefonnummer"), max_length=32, null=True, blank=True
    )
    gender = models.PositiveSmallIntegerField(
        _("Geschlecht"), choices=GENDER_CHOICES, null=True, blank=True
    )
    birthday = models.DateField(_("Geburtstag"), null=True, blank=True)


class OwnerAware(models.Model):
    """Abstract Mixin – verleiht einem Model eine Owner-Beziehung."""

    class Meta:
        abstract = True

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Besitzer"),
        on_delete=models.PROTECT,
    )

    def is_owned_by(self, user):
        return self.owner == user

    def is_managable_by(self, user):
        return self.is_owned_by(user)


class OwnerAwareQuerySetMixin:
    """QuerySet-Mixin mit owned_by() Filter."""

    def owned_by(self, owner):
        return self.filter(owner=owner)
