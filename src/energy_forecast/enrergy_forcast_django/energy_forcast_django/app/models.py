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

    label = models.CharField(choices=TypeDeProduction)
    date = models.DateTimeField(
        default=django.utils.timezone.now(),
        blank=False,
        verbose_name="Date pour laquelle cette prediction est faite."
    )
    valeur = models.FloatField(verbose_name="""Valeur de la prediction.""", default=None, null=True)

