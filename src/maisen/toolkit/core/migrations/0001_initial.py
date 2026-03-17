import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="AddressData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")),
                ("modified", models.DateTimeField(auto_now=True, verbose_name="Bearbeitet")),
                ("parent_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("default", "Standard"),
                            ("delivery", "Lieferadresse"),
                            ("invoice", "Rechnungsadresse"),
                        ],
                        default="default",
                        max_length=16,
                        verbose_name="Typ",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=256, null=True, verbose_name="Titel")),
                ("salutation", models.CharField(blank=True, max_length=256, null=True, verbose_name="Anrede")),
                ("company", models.CharField(blank=True, max_length=256, null=True, verbose_name="Firma")),
                ("person", models.CharField(blank=True, max_length=256, null=True, verbose_name="Person")),
                ("street", models.CharField(blank=True, max_length=256, null=True, verbose_name="Straße")),
                ("number", models.CharField(blank=True, max_length=256, null=True, verbose_name="Nummer")),
                ("zip", models.CharField(blank=True, max_length=6, null=True, verbose_name="PLZ")),
                ("city", models.CharField(blank=True, max_length=256, null=True, verbose_name="Stadt")),
                ("district", models.CharField(blank=True, max_length=256, null=True, verbose_name="Bezirk")),
                ("country", models.CharField(blank=True, max_length=256, null=True, verbose_name="Land")),
                ("phone", models.CharField(blank=True, max_length=256, null=True, verbose_name="Telefon")),
                ("phone_home", models.CharField(blank=True, max_length=256, null=True, verbose_name="Telefon Privat")),
                ("phone_mobile", models.CharField(blank=True, max_length=256, null=True, verbose_name="Telefon Mobil")),
                ("fax", models.CharField(blank=True, max_length=256, null=True, verbose_name="Fax")),
                ("email", models.CharField(blank=True, max_length=256, null=True, verbose_name="E-Mail-Adresse")),
                ("uid", models.CharField(blank=True, max_length=256, null=True, verbose_name="UID")),
                ("web", models.URLField(blank=True, null=True, verbose_name="Website")),
                (
                    "parent_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Adresse",
                "verbose_name_plural": "Adressen",
                "db_table": "addresses_addressdata",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="GeoLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt")),
                ("modified", models.DateTimeField(auto_now=True, verbose_name="Bearbeitet")),
                ("parent_id", models.PositiveIntegerField(blank=True, null=True)),
                ("lat", models.FloatField(verbose_name="Lat")),
                ("lng", models.FloatField(verbose_name="Lng")),
                ("zoom", models.IntegerField(blank=True, null=True, verbose_name="Zoom")),
                ("timestamp", models.DateTimeField(blank=True, null=True, verbose_name="Zeitstempel")),
                (
                    "parent_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Geo-Koordinaten",
                "verbose_name_plural": "Geo-Koordinaten",
                "db_table": "addresses_geolocation",
                "ordering": ("-timestamp", "-id"),
            },
        ),
        migrations.AddIndex(
            model_name="geolocation",
            index=models.Index(fields=["lat", "lng"], name="addresses_g_lat_a3b8e6_idx"),
        ),
        migrations.AddConstraint(
            model_name="geolocation",
            constraint=models.UniqueConstraint(
                fields=("parent_type", "parent_id", "lat", "lng", "timestamp"),
                name="unique_geolocation_per_parent",
            ),
        ),
    ]
