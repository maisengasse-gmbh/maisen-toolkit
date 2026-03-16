from django.contrib import admin
from django.urls import include, path

from maisen.toolkit.totp import urls as totp_urls

urlpatterns = [
    path("admin/totp/", include((totp_urls, "totp"), namespace="totp")),
    path("admin/", admin.site.urls),
]
