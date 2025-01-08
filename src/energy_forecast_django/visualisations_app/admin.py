"""
    On defini ici les informations et actions accessible depuis le panel admin de l'application.

    Voir https://docs.djangoproject.com/en/5.1/ref/contrib/admin/
"""
import typing

from django.contrib import admin
from . import models

@admin.register(models.PredictedConsumption)
class PredictionAdmin(admin.ModelAdmin):
    """Class admin pour les predictions."""
    list_display: typing.ClassVar[list[str]] = [
        "forecasted_for", "predicted_at", "fetched_at", "predicted_consumption"
    ]
    list_filter: typing.ClassVar[list[str]] = [
        "forecasted_for", "predicted_at", "fetched_at", "predicted_consumption"
    ]
    search_fields: typing.ClassVar[list[str]] = ["forecasted_for", "predicted_at"]
