from datetime import timezone
from datetime import datetime

from django.db import models
from django.db.models import Model


class SoftDeletionQuerySet(models.QuerySet):
    """Queryset for models with support of soft deletion."""

    def delete(self):
        """Soft deletion. Mark objects with deleted_at date and time"""
        return super().update(deleted_at=datetime.now(timezone.UTC))

    def hard_delete(self):
        """Complete deletion of objects."""
        return super().delete()

    def alive(self):
        """Provide queryset of active (not soft deleted) objects"""
        return self.filter(deleted_at=None)

    def dead(self):
        """Provide queryset of soft deleted objects"""
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager.from_queryset(SoftDeletionQuerySet)):  # type: ignore
    """Manager for models with support of soft deletion."""

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop("alive_only", True)
        super().__init__()

    def get_queryset(self):
        """Get queryset of objects due to alive_only option"""
        qs = super().get_queryset()
        return qs.alive() if self.alive_only else qs

    def hard_delete(self):
        """Complete deletion of objects."""
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = datetime.now(UTC)
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)


class TimestampedModel(SoftDeletionModel):
    """
    A timestamped soft delete base model
    """

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def object_type(self):
        return self.__class__.__name__.lower()


# --------------------------------------------------------------------------------
# Model related utility methods
# --------------------------------------------------------------------------------
def has_related_object(obj: type[Model], name):
    return hasattr(obj, name)
