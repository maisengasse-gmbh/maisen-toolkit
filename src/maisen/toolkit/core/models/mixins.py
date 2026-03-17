from django.contrib.contenttypes import fields as generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampMixin(models.Model):
    """Abstract Mixin mit created/modified Timestamps."""

    class Meta:
        abstract = True
        ordering = ["-id"]

    created = models.DateTimeField(_("Erstellt"), auto_now_add=True, editable=False)
    modified = models.DateTimeField(_("Bearbeitet"), auto_now=True, editable=False)

    def __str__(self):
        return str(self.id)


class DublinCore(TimeStampMixin):
    """Abstract Mixin: TimeStampMixin + title + description."""

    class Meta(TimeStampMixin.Meta):
        abstract = True

    title = models.CharField(_("Titel"), null=True, blank=True, max_length=255)
    description = models.TextField(_("Beschreibung"), null=True, blank=True)

    def __str__(self):
        return self.title or str(self.id)


class Annotation(TimeStampMixin):
    """Abstract Mixin mit GenericForeignKey fuer polymorphe Beziehungen."""

    class Meta(TimeStampMixin.Meta):
        abstract = True

    parent_type = models.ForeignKey(
        ContentType, blank=True, null=True, on_delete=models.CASCADE
    )
    parent_id = models.PositiveIntegerField(blank=True, null=True)
    parent = generic.GenericForeignKey(ct_field="parent_type", fk_field="parent_id")
