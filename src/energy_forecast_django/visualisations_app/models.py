import plotly.express as px
import plotly
import pandas as pd
import django.utils.timezone
from django.db import models

"""
    On definit ici toutes les modèls (qui sont de class basées sur la class standard 'Model' qui representent notre BDD.
    
    Voir https://docs.djangoproject.com/en/5.1/topics/db/models/
"""

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

    @property
    def formatted_date(self) -> str:
        return self.date.strftime("%a %d %B %Y")

class Eco2MixObservation(models.Model):
    """Storages the data from the Eco2Mix API."""
    at_instant = models.DateTimeField(
        default=django.utils.timezone.now,
        blank=False,
        verbose_name="Date pour laquelle cette observation est faite."
   )
    consommation = models.FloatField(verbose_name="Consommation en MW", default=None, null=True)
    eolien = models.FloatField(verbose_name="Production éolienne en MW", default=None, null=True)
    solaire = models.FloatField(verbose_name="Production solaire en MW", default=None, null=True)

class PredictedConsumption(models.Model):
    """Storages the data from the consumption prediction.
    The data is provided by RTE.
    """
    forecasted_for = models.DateTimeField(
        default=None,
        blank=False,
        verbose_name="Date pour laquelle cette prediction est faite."
    )
    predicted_at = models.DateTimeField(
        default=None,
        blank=False,
        verbose_name="Date de calcul de la prediction."
    )
    fetched_at = models.DateTimeField(
        default=django.utils.timezone.now,
        blank=False,
        verbose_name="Date de récupération de la prediction."
    )
    predicted_consumption = models.FloatField(
        verbose_name="Valeur de la prediction de la consommation nationale (MW)", default=None, null=True
    )

def generate_graph(
        prediction_model: models.Model,
        x_feature: str,x_label: str,
        y_feature: str|None, y_label: str|None,
        figure_function: plotly.graph_objs._figure
):
    x_values: list[float | None] = list(
        prediction_model.objects.values_list(x_feature, flat=True)
    )
    y_values: list[django.utils.timezone.datetime | None] = list(
        prediction_model.objects.values_list(y_feature, flat=True)
    )
    data = pd.DataFrame(
        {x_label: x_values, y_label: y_values}
    )
    if figure_function not in [px.bar, px.scatter]:
        AttributeError("plot_type can only be bar or scatter")
    return figure_function(
        data_frame=data, x=x_label, y=y_label
    )

def style_graph(figure: plotly.graph_objs._figure.Figure)->str:
    #TODO Add styling parameters to reproduce the graphs currently used
    return plotly.offline.plot(figure, output_type="div")