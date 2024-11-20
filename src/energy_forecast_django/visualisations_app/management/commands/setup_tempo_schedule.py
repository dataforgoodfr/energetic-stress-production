# visualisations_app/management/commands/setup_tempo_schedule.py
from django.core.management.base import BaseCommand
from visualisations_app.tasks.daily_prediction import schedule_tempo_predictions

class Command(BaseCommand):
    help = 'Set up scheduled Tempo predictions'

    def handle(self, *args, **kwargs):
        schedule_tempo_predictions()
        self.stdout.write(self.style.SUCCESS('Successfully scheduled Tempo predictions'))
