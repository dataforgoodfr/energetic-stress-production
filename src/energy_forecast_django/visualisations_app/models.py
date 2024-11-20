import django.utils.timezone
from django.db import models

"""
    On definit ici toutes les modèls (qui sont de class basées sur la class standard 'Model' qui representent notre BDD.
    
    Voir https://docs.djangoproject.com/en/5.1/topics/db/models/
"""

class Prediction(models.Model):
    """Point de donnée issue d'une prediction."""
    
    class TypeDeProduction(models.TextChoices):
        """Label des type de prediction."""
        EOLIEN = "Point de prediction eolien"
        SOLAIR = "Point de prediction solair"

    label = models.CharField(choices=TypeDeProduction.choices, verbose_name="Type de production", max_length=30)
    date = models.DateTimeField(
        default=django.utils.timezone.now,
        blank=False,
        verbose_name="Date pour laquelle cette prediction est faite."
    )
    valeur = models.FloatField(verbose_name="""Valeur de la prediction.""", default=None, null=True)

class TempoClassification(models.Model):
    """Point de donnée issue d'une classification tempo."""

    class TypeDeJour(models.TextChoices):
        """Label des type de jour."""
        BLUE = "BLUE"
        RED = "RED"
        WHITE = "WHITE"

    date = models.DateTimeField(
        default=django.utils.timezone.now,
        blank=False,
        verbose_name="Date pour laquelle cette classification est faite."
    )
    by_RTE = models.CharField(choices=TypeDeJour.choices, verbose_name="Classification par RTE", max_length=5)
    ours_J_1 = models.CharField(choices=TypeDeJour.choices, verbose_name="Notre classification J-1", max_length=5)
    ours_J_2 = models.CharField(choices=TypeDeJour.choices, verbose_name="Notre classification J-2", max_length=5)
    ours_J_3 = models.CharField(choices=TypeDeJour.choices, verbose_name="Notre classification J-3", max_length=5)
