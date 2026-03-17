from django.db import models
from django.utils.translation import gettext_lazy as _


class TotpUserMixin(models.Model):
    """Abstract Mixin – dem eigenen UserAccount-Model hinzufügen."""

    totp_secret = models.CharField(max_length=32, blank=True, default="")
    totp_enabled = models.BooleanField(default=False)

    class Meta:
        abstract = True


class GroupTotpRequirementMixin(models.Model):
    """Abstract Mixin – dem eigenen Projekt als konkretes Model hinzufügen."""

    class Meta:
        abstract = True
        verbose_name = _("Gruppen-TOTP-Pflicht")
        verbose_name_plural = _("Gruppen-TOTP-Pflichten")

    group = models.OneToOneField(
        "auth.Group",
        on_delete=models.CASCADE,
        related_name="totp_requirement",
    )
    totp_required = models.BooleanField(
        default=False,
        verbose_name=_("TOTP erforderlich"),
    )

    def __str__(self):
        status = "erforderlich" if self.totp_required else "optional"
        return f"{self.group.name} – TOTP {status}"
