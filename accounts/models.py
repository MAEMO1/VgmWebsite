from django.contrib.auth.models import AbstractUser
from django.db import models


class Mosque(models.Model):
    """Core mosque model used for RBAC scoping."""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    )

    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending')

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class User(AbstractUser):
    """Custom user model with role-based metadata."""

    ROLE_CHOICES = (
        ('GAST', 'Gast'),
        ('LID', 'Lid'),
        ('MOSKEE_BEHEERDER', 'Moskee beheerder'),
        ('BEHEERDER', 'Beheerder'),
    )

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='GAST')
    email_verified = models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    managed_mosques = models.ManyToManyField(Mosque, blank=True, related_name='managers')

    @property
    def is_admin(self) -> bool:
        return self.role == 'BEHEERDER'

    def manages_mosque(self, mosque_id: str) -> bool:
        return self.role in {'MOSKEE_BEHEERDER', 'BEHEERDER'} and (
            self.role == 'BEHEERDER' or self.managed_mosques.filter(pk=mosque_id).exists()
        )
