from django.contrib.contenttypes import fields as generic
from django.db import models
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from .addresses import AddressAware
from .mixins import Annotation


class GeoLocationQuerySet(models.QuerySet):
    def get_nearby_coords(self, lat, lng, max_distance=None):
        """Sortiert nach Entfernung (Great Circle Distance in km)."""
        gcd_formula = (
            "6371 * acos(cos(radians(%s)) * "
            "cos(radians(lat)) "
            "* cos(radians(lng) - radians(%s)) + "
            "sin(radians(%s)) * sin(radians(lat)))"
        )
        distance_raw_sql = RawSQL(gcd_formula, (lat, lng, lat))
        qs = self.annotate(distance=distance_raw_sql).order_by("distance")
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
        return qs


class AbstractGeoLocation(Annotation, AddressAware):
    """Abstract Base fuer Geo-Koordinaten mit GenericForeignKey."""

    class Meta(Annotation.Meta):
        abstract = True
        verbose_name = _("Geo-Koordinaten")
        verbose_name_plural = _("Geo-Koordinaten")
        ordering = ("-timestamp", "-id")

    objects = GeoLocationQuerySet.as_manager()

    lat = models.FloatField(_("Lat"))
    lng = models.FloatField(_("Lng"))
    zoom = models.IntegerField(_("Zoom"), null=True, blank=True)
    timestamp = models.DateTimeField(_("Zeitstempel"), null=True, blank=True)

    def as_dict(self):
        return {"lat": self.lat, "lng": self.lng, "zoom": self.zoom}

    def __str__(self):
        return "%.5f , %.5f" % (self.lat, self.lng)


class GeoLocation(AbstractGeoLocation):
    """Konkreter Default fuer Geo-Koordinaten."""

    class Meta(AbstractGeoLocation.Meta):
        db_table = "addresses_geolocation"
        indexes = [
            models.Index(fields=["lat", "lng"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["parent_type", "parent_id", "lat", "lng", "timestamp"],
                name="unique_geolocation_per_parent",
            ),
        ]


class GeoLocationAware(models.Model):
    """Abstract Mixin – verleiht einem Model GeoLocation-Beziehungen."""

    class Meta:
        abstract = True

    geolocations = generic.GenericRelation(
        GeoLocation, object_id_field="parent_id", content_type_field="parent_type"
    )

    def set_geolocation(self, **kw):
        existing = self.get_geolocation()
        if existing:
            for key, value in kw.items():
                setattr(existing, key, value)
                existing.save()
                self.save()
        else:
            self.geolocations.create(**kw)

    def get_geolocation(self):
        try:
            return self.geolocations.get()
        except GeoLocation.DoesNotExist:
            return None
