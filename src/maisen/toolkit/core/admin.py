from django import forms
from django.contrib.contenttypes import admin as generic

from maisen.toolkit.core.models import AddressData, GeoLocation


class AnnotationInlineMixin:
    """Mixin fuer Admin-Inlines mit GenericForeignKey."""

    ct_field = "parent_type"
    ct_fk_field = "parent_id"


class AddressInlineForm(forms.ModelForm):
    class Meta:
        model = AddressData
        fields = (
            "type",
            "title",
            "person",
            "email",
            "web",
            "phone",
            "street",
            "number",
            "zip",
            "city",
        )


class SingleAddressInlineForm(forms.ModelForm):
    class Meta:
        model = AddressData
        fields = (
            "title",
            "person",
            "email",
            "web",
            "phone",
            "street",
            "number",
            "zip",
            "city",
        )


class AddressInline(AnnotationInlineMixin, generic.GenericStackedInline):
    form = AddressInlineForm
    model = AddressData


class SingleAddressInline(AddressInline):
    form = SingleAddressInlineForm
    extra = 1
    max_num = 1


class GeoLocationInline(AnnotationInlineMixin, generic.GenericTabularInline):
    fields = ("lat", "lng")
    model = GeoLocation
    extra = 1
    max_num = 1
