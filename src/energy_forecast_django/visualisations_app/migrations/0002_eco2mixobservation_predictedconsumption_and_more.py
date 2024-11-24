# Generated by Django 4.2.16 on 2024-11-23 13:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('visualisations_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Eco2MixObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at_instant', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date pour laquelle cette observation est faite.')),
                ('consommation', models.FloatField(default=None, null=True, verbose_name='Consommation en MW')),
                ('eolien', models.FloatField(default=None, null=True, verbose_name='Production éolienne en MW')),
                ('solaire', models.FloatField(default=None, null=True, verbose_name='Production solaire en MW')),
            ],
        ),
        migrations.CreateModel(
            name='PredictedConsumption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecasted_for', models.DateTimeField(default=None, verbose_name='Date pour laquelle cette prediction est faite.')),
                ('predicted_at', models.DateTimeField(default=None, verbose_name='Date de calcul de la prediction.')),
                ('fetched_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de récupération de la prediction.')),
                ('predicted_consumption', models.FloatField(default=None, null=True, verbose_name='Valeur de la prediction de la consommation nationale (MW)')),
            ],
        ),
        migrations.RenameField(
            model_name='prediction',
            old_name='date',
            new_name='forecasted_for',
        ),
        migrations.AddField(
            model_name='prediction',
            name='predicted_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de calcul de la prediction.'),
        ),
    ]
