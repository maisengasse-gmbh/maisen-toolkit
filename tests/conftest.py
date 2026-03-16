import pytest


@pytest.fixture
def admin_user(db):
    """Superuser für Tests."""
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_superuser(
        username="admin", password="test"
    )


@pytest.fixture
def normal_user(db):
    """Normaler User für Tests."""
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        username="user", password="test"
    )
