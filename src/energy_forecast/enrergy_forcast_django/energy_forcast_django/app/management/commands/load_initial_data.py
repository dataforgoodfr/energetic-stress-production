# app/management/commands/load_initial_data.py
import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from energy_forecast.enrergy_forcast_django.app.models import TempoClassification
from energy_forecast import ROOT_DIR

class Command(BaseCommand):
    help = 'Load initial data from CSV files'

    def handle(self, *args, **kwargs):
        # Clear existing data
        TempoClassification.objects.all().delete()
        
        # Load data from CSV
        datafile = ROOT_DIR / 'data' / 'gold' / 'our_tempo_prediction.csv'
        with open(datafile, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(row)
                TempoClassification.objects.create(
                    date=timezone.datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S'),
                    by_RTE=row['by_RTE'],
                    ours_J_1=row['ours_J_1'],
                    ours_J_2=row['ours_J_2'],
                    ours_J_3=row['ours_J_3']
                )
                
        self.stdout.write(self.style.SUCCESS('Successfully loaded data'))
