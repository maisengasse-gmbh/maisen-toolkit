import re

from django.contrib.contenttypes import fields as generic
from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import Annotation


class AbstractAddressData(Annotation):
    """Abstract Base fuer Adressdaten mit GenericForeignKey."""

    class Meta(Annotation.Meta):
        abstract = True
        verbose_name = _("Adresse")
        verbose_name_plural = _("Adressen")
        ordering = ("id",)

    TYPE_DEFAULT = "default"
    TYPE_DELIVERY = "delivery"
    TYPE_INVOICE = "invoice"

    TYPES = (TYPE_DEFAULT, TYPE_DELIVERY, TYPE_INVOICE)

    TYPE_SET = (
        (TYPE_DEFAULT, _("Standard")),
        (TYPE_DELIVERY, _("Lieferadresse")),
        (TYPE_INVOICE, _("Rechnungsadresse")),
    )

    type = models.CharField(
        _("Typ"), max_length=16, choices=TYPE_SET, default=TYPE_DEFAULT
    )
    title = models.CharField(_("Titel"), max_length=256, blank=True, null=True)
    salutation = models.CharField(_("Anrede"), max_length=256, blank=True, null=True)
    company = models.CharField(_("Firma"), max_length=256, blank=True, null=True)
    person = models.CharField(_("Person"), max_length=256, blank=True, null=True)
    street = models.CharField(_("Straße"), max_length=256, blank=True, null=True)
    number = models.CharField(_("Nummer"), max_length=256, blank=True, null=True)
    zip = models.CharField(_("PLZ"), max_length=6, blank=True, null=True)
    city = models.CharField(_("Stadt"), max_length=256, blank=True, null=True)
    district = models.CharField(_("Bezirk"), max_length=256, blank=True, null=True)
    country = models.CharField(_("Land"), max_length=256, blank=True, null=True)
    phone = models.CharField(_("Telefon"), max_length=256, blank=True, null=True)
    phone_home = models.CharField(
        _("Telefon Privat"), max_length=256, blank=True, null=True
    )
    phone_mobile = models.CharField(
        _("Telefon Mobil"), max_length=256, blank=True, null=True
    )
    fax = models.CharField(_("Fax"), max_length=256, blank=True, null=True)
    email = models.CharField(
        _("E-Mail-Adresse"), max_length=256, blank=True, null=True
    )
    uid = models.CharField(_("UID"), max_length=256, blank=True, null=True)
    web = models.URLField(_("Website"), blank=True, null=True)

    def as_dict(self, props={}):
        d = {}
        for field in self._meta.fields:
            d[field.name] = getattr(self, field.name)
        d.update(props)
        return d

    def save(self, *args, **kw):
        existing = self.parent.get_address(self.type)
        if existing and existing != self:
            raise TypeError(
                "AddressData of sametype already exists", self.type, self.parent
            )
        else:
            super().save(*args, **kw)

    def get_shortaddress(self):
        short = self.city
        if self.zip:
            short = "%s %s" % (self.zip, short)
        if self.street:
            short = "%s, %s" % (self.get_street_and_number(), short)
        return short

    def __str__(self):
        return "<AddressData %s>" % (self.get_shortaddress())

    def get_street_and_number(self):
        parts = [self.street]
        if self.number:
            parts.append(self.number)
        return " ".join(parts)

    def get_street(self):
        if not self.number:
            parts = re.compile(r"^(.+)\s+(\d+)$").findall(self.street)
            if len(parts):
                return parts[0][0]
        return self.street

    def get_number(self):
        if not self.number:
            parts = re.compile(r"^(.+)\s+(\d+)$").findall(self.street)
            if len(parts):
                return parts[0][1]
        return self.number


class AddressData(AbstractAddressData):
    """Konkreter Default fuer Adressdaten."""

    class Meta(AbstractAddressData.Meta):
        db_table = "addresses_addressdata"


class AddressAware(models.Model):
    """Abstract Mixin – verleiht einem Model Adress-Beziehungen."""

    class Meta:
        abstract = True

    addresses = generic.GenericRelation(
        AddressData, object_id_field="parent_id", content_type_field="parent_type"
    )

    def set_address(self, type=AddressData.TYPE_DEFAULT, **kw):
        existing = self.get_address(type)
        if existing:
            for key, value in list(kw.items()):
                setattr(existing, key, value)
                existing.save()
                self.save()
        else:
            self.addresses.create(type=type, **kw)

    def get_address(self, t=AddressData.TYPE_DEFAULT):
        try:
            return self.addresses.get(type=t)
        except AddressData.DoesNotExist:
            return None
