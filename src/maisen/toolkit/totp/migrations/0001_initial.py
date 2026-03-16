from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupTotpRequirement",
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
                (
                    "totp_required",
                    models.BooleanField(
                        default=False, verbose_name="TOTP erforderlich"
                    ),
                ),
                (
                    "group",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="totp_requirement",
                        to="auth.group",
                    ),
                ),
            ],
            options={
                "verbose_name": "Gruppen-TOTP-Pflicht",
                "verbose_name_plural": "Gruppen-TOTP-Pflichten",
            },
        ),
    ]
