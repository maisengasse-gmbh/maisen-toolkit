# maisen.toolkit.core — Basis-Models und Mixins

Grundlegende Abstract Mixins (Timestamps, Dublin Core, Annotation) sowie konkrete Adress- und GeoLocation-Models mit GenericForeignKey-Support.

## Quick Start

```python
INSTALLED_APPS = [
    ...
    "maisen.toolkit.core",
]
```

```bash
python manage.py migrate maisen_core
```

## Abstract Mixins

### TimeStampMixin

Timestamps fuer alle Models.

```python
from maisen.toolkit.core.models import TimeStampMixin

class MyModel(TimeStampMixin):
    name = models.CharField(max_length=100)
    # erbt: created (auto_now_add), modified (auto_now)
```

### DublinCore

TimeStampMixin + title + description.

```python
from maisen.toolkit.core.models import DublinCore

class Article(DublinCore):
    content = models.TextField()
    # erbt: created, modified, title, description
```

### Annotation

TimeStampMixin + GenericForeignKey (parent_type, parent_id, parent).

```python
from maisen.toolkit.core.models import Annotation

class Comment(Annotation):
    text = models.TextField()
    # erbt: created, modified, parent (GenericForeignKey)
```

## Adressen

### AddressData (Concrete Default)

Konkretes Model fuer Adressdaten, verbunden ueber GenericForeignKey.

```python
from maisen.toolkit.core.models import AddressAware

class Customer(AddressAware):
    name = models.CharField(max_length=100)

# Nutzung:
customer.set_address(street="Hauptstr.", number="1", city="Wien", zip="1010")
address = customer.get_address()
```

### AbstractAddressData

Fuer eigene Erweiterungen:

```python
from maisen.toolkit.core.models import AbstractAddressData

class ExtendedAddress(AbstractAddressData):
    floor = models.CharField(max_length=10, blank=True)
    apartment = models.CharField(max_length=10, blank=True)
```

## GeoLocation

### GeoLocation (Concrete Default)

Konkretes Model fuer Geo-Koordinaten.

```python
from maisen.toolkit.core.models import GeoLocationAware

class Site(GeoLocationAware):
    name = models.CharField(max_length=100)

# Nutzung:
site.set_geolocation(lat=47.26, lng=11.39)
geo = site.get_geolocation()

# Nearby-Suche:
from maisen.toolkit.core.models import GeoLocation
nearby = GeoLocation.objects.get_nearby_coords(47.26, 11.39, max_distance=10)
```

## Accounts Mixins

### UserProfileMixin

Gemeinsame User-Profil-Felder (phone, gender, birthday).

```python
from maisen.toolkit.core.models import UserProfileMixin

class UserAccount(AbstractUser, UserProfileMixin):
    ...
    # erbt: phone, gender, birthday
```

### OwnerAware + OwnerAwareQuerySetMixin

Owner-Beziehung fuer Models mit `is_owned_by()`/`is_managable_by()`.

```python
from maisen.toolkit.core.models import OwnerAware, OwnerAwareQuerySetMixin

class ProjectQuerySet(OwnerAwareQuerySetMixin, models.QuerySet):
    pass

class Project(OwnerAware):
    objects = ProjectQuerySet.as_manager()
    title = models.CharField(max_length=100)

# Nutzung:
project.is_owned_by(user)
Project.objects.owned_by(user)
```

## Admin-Inlines

```python
from maisen.toolkit.core.admin import AddressInline, SingleAddressInline, GeoLocationInline

class CustomerAdmin(admin.ModelAdmin):
    inlines = [SingleAddressInline, GeoLocationInline]
```
