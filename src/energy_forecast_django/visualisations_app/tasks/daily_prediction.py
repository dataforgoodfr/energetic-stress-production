
import logging

import numpy as np

# import dotenv
import pandas as pd

from energy_forecast import ROOT_DIR
from energy_forecast.consumption_forecast import PredictionForecastAPI
from energy_forecast.eco2mix import get_data as get_eco2mix_data
from energy_forecast.enr_production_model import ENRProductionModel
from energy_forecast.meteo import (
    ArpegeSimpleAPI,
    aggregates_observations,
    download_observations_all_departments,
)
from energy_forecast.performances import expires_after, memory
from energy_forecast.tempo_rte import TempoPredictor, TempoSignalAPI
from visualisations_app.models import TempoClassification, Eco2MixObservation, PredictedConsumption, Prediction

logger = logging.getLogger(__name__)
TODAY = pd.Timestamp.now().date()
gold_dir = ROOT_DIR / "data" / "gold"
# envfile = ROOT_DIR / ".env"
# dotenv.load_dotenv(envfile)

if not gold_dir.exists():
    gold_dir.mkdir()

def fetch_history_data() -> pd.DataFrame:
    """Return the history data from the eco2mix API.

    WARNING : the API is not very reliable and the data is not always returend.
    TODO : add validation to check if the data is returned.
    """
    now = pd.Timestamp.now()
    one_year_ago = now.date() - pd.DateOffset(years=1) - pd.DateOffset(month=9, day=1)
    last_entry = Eco2MixObservation.objects.last()
    if last_entry:
        start = last_entry.at_instant
        
    else :
        start = one_year_ago
        
    ecomix_data = get_eco2mix_data(start=start, end=now)[["consommation", "eolien", "solaire"]]
    ecomix_data_no_duplicates = ecomix_data[~ecomix_data.index.duplicated()]
    # upload to database
    Eco2MixObservation.objects.bulk_create([
        Eco2MixObservation(
            at_instant=idx,
            consommation=row['consommation'],
            eolien=row['eolien'],
            solaire=row['solaire']
        ) for idx, row in ecomix_data_no_duplicates.iterrows()
    ], ignore_conflicts=True)
    # load all the needed data from one year ago
    ecomix_data_no_duplicates_raw = Eco2MixObservation.objects.filter(at_instant__gte=one_year_ago).values()
    ecomix_data_no_duplicates = pd.DataFrame(ecomix_data_no_duplicates_raw).set_index("at_instant").drop(columns=["id"])
    return ecomix_data_no_duplicates


@memory.cache(cache_validation_callback=expires_after(hours=2))
def fetch_ret_consumption_forecast():
    """Fetch the consumption forecast from the RTE API.

    TODO : here the function only uses the weekly forecast.
    The short_term forecast could be used as well.
    It should be slightly more accurate.

    However, the short term forecast is only available for the next 2 days (D-1 and D-2).
    Hence a merge with the weekly forecast is needed.

    """

    client = PredictionForecastAPI()
    today = pd.Timestamp.now().date()
    stored_consumtion_forecast = PredictedConsumption.objects.filter(fetched_at__gte=today).values()
    if stored_consumtion_forecast:
        fetched_at = stored_consumtion_forecast[0]['fetched_at']
        if fetched_at.date() == today:
            return pd.DataFrame(stored_consumtion_forecast).set_index("forecasted_for").drop(columns=["id"])
    consumption_forecast = client.get_weekly_forecast(today, horizon="2d")
    consumption_forecast["fetched_at"] = pd.Timestamp.now(tz="UTC")
    # upload to database
    for idx, row in consumption_forecast.iterrows():
        PredictedConsumption.objects.bulk_create([
            PredictedConsumption(
                forecasted_for=idx,
                predicted_at=row['predicted_at'],
                fetched_at=row['fetched_at'],
                predicted_consumption=row['predicted_consumption']
            ) for idx, row in consumption_forecast.iterrows()
        ], ignore_conflicts=True)
    return consumption_forecast


def fetch_mf_sun_forecast():
    client = ArpegeSimpleAPI(date=TODAY)
    mf_sun_deps = client.departement_sun()
    return mf_sun_deps


def fetch_mf_wind_forecast():
    client = ArpegeSimpleAPI(date=TODAY)
    mf_wind_deps = client.departement_wind()
    return mf_wind_deps


def compute_our_enr_forecast():
    """Predict the renewable energy production."""
    # look in the database
    today = pd.Timestamp.now(tz="UTC").floor("D")
    last_prediction = Prediction.objects.filter(predicted_at__gte=today).values()
    if last_prediction:
        return pd.DataFrame(last_prediction).set_index("forecasted_for").drop(columns=["id"])
    
    # Fetch the forecasts
    sun_forecast = fetch_mf_sun_forecast()
    wind_forecast = fetch_mf_wind_forecast()

    model = ENRProductionModel.load(filename="model_departements.pkl")
    our_enr_forecast = model.predict(sun_flux=sun_forecast, wind_speed=wind_forecast)
    our_enr_forecast = our_enr_forecast.rename(
        columns={
            "sun": "solaire",
            "wind": "eolien",
        }
    )
    # cleanup
    our_enr_forecast = our_enr_forecast.dropna()
    our_enr_forecast.rename(columns={"sun": "SOLAIR", "wind": "EOLIEN"}, inplace=True)
    long_enr_forecast = our_enr_forecast.melt(var_name="label",
                                              value_name="valeur",
                                              ignore_index=False)
    # upload to database
    predicted_at = pd.Timestamp.now(tz="UTC")
    predictions = [
        Prediction(
            forecasted_for=idx.tz_localize("UTC"),
            label=row['label'],
            valeur=row['valeur'],
            predicted_at=predicted_at
        ) for idx, row in long_enr_forecast.iterrows()
    ]
    Prediction.objects.bulk_create(predictions, ignore_conflicts=True)
    return our_enr_forecast.tz_localize("UTC")


@memory.cache(cache_validation_callback=expires_after(hours=2))
def fetch_temperature():
    """Limitation : there only the observed temperature is used.

    TODO : add the forecasted mean daily temperature.
    TODO : make sure the last day is complete (the observations are not always available for the current day).
    """
    files = download_observations_all_departments()
    cut_before = TODAY - pd.DateOffset(years=1) - pd.DateOffset(month=9, day=1)
    cut_before = TODAY - pd.DateOffset(years=1) - pd.DateOffset(month=9, day=1)
    daily_temperature = aggregates_observations(files, cut_before=cut_before).tz_localize("Europe/Paris")
    return daily_temperature


def get_all_data():
    logger.info("Fetching all the data")
    logger.info("Fetching the history data")
    ecomix_data = fetch_history_data()
    logger.info("Fetching the consumption forecast")
    consumption_forecast = fetch_ret_consumption_forecast()
    logger.info("Fetching the renewable energy forecast")
    our_enr_forecast = compute_our_enr_forecast()
    logger.info("Fetching the temperature")
    daily_temperature = fetch_temperature()
    logger.info("Fetching the tempo signal")
    tempos = get_history_tempo_days()
    logger.info("Merging all the data")

    prediction_data = pd.concat([consumption_forecast.resample("h").mean(), our_enr_forecast], axis=1).dropna()
    all_data = pd.concat([ecomix_data.resample("h").mean(),
                          prediction_data], axis=0)
    all_data.index = pd.to_datetime(all_data.index, utc=True).tz_convert("Europe/Paris")
    origin = all_data.index[0] + pd.DateOffset(hour=6)
    all_daily_data = all_data.resample("h").mean().resample("D", origin=origin).sum()[1:-1]
    all_daily_data.index = all_daily_data.index.floor("D")

    data = pd.concat([
        all_daily_data,
        tempos["value"].rename("Type_de_jour_TEMPO"),
        daily_temperature.rename("temperature")
        ],
                     axis=1)
    return data


def generate_features(data, inplace=False):
    logger.info("Generating features")
    if not inplace:
        data = data.copy()
    data["production_nette"] = data["consommation"] - (data["eolien"] + data["solaire"])
    quantils = (
        data["production_nette"]
        .rolling(365, center=False)
        .aggregate({"q40": lambda x: x.quantile(0.4), "q80": lambda x: x.quantile(0.8)})
        .bfill()
    )
    data["production_nette_q40"] = quantils["q40"]
    data["production_nette_q80"] = quantils["q80"]
    data["mean_temp_q30"] = (
        data["temperature"].ffill().rolling(365, center=False).aggregate(lambda x: x.quantile(0.3)).bfill().ffill()
    )
    return data


def get_history_tempo_days():
    """Get the tempo signal since the start of the tempo year."""
    client = TempoSignalAPI()
    start_date = TODAY - pd.DateOffset(day=1, month=9)
    after_tomorrow = TODAY + pd.DateOffset(days=2)
    history_tempo = client.get_data(start_date=start_date, end_date=after_tomorrow).sort_index(ascending=True)
    return history_tempo


def pred_to_correct_column(data):
    """
    This function swaps prediction to correct predictions columns :
    j-1 predictions to column 'our_tempo_J-1'
    j-2 predictions to column 'our_tempo_J-2'
    j-3 predictions to column 'our_tempo_J-3'

    Removing useless columns.
    """
    data["day_from_td"] = (data.index - pd.to_datetime(TODAY)).days
    data["our_tempo_J-1"] = np.where(data["day_from_td"] <= 1, data["our_tempo"], None)
    data["our_tempo_J-2"] = np.where(data["day_from_td"] == 2, data["our_tempo"], None)
    data["our_tempo_J-3"] = np.where(data["day_from_td"] == 3, data["our_tempo"], None)
    del data["day_from_td"]
    del data["our_tempo"]
    return data


def write_pred(data):
    """
    Save results from tempo predictions.
    Handles assignment to the right column with the pred_to_correct_column function.
    Completes the None values in the current file if new predictions are made.
    Combine first duplicates columns in certain cases,
    so security is added if predictions have already been calculated on the same day.
    """

    logger.info("Writting predictions")
    data = pred_to_correct_column(data)
    data.index = data.index.date
    data.index.name = "date"
    # Update or create records
    for idx, row in data.iterrows():
        TempoClassification.objects.update_or_create(
            date=idx,
            defaults={
                'by_RTE': row['Type_de_jour_TEMPO'],
                'ours_J_1': row['our_tempo_J-1'],
                'ours_J_2': row['our_tempo_J-2'], 
                'ours_J_3': row['our_tempo_J-3']
            }
        )
    logger.info("Predictions saved to database")
    return True

def run_tempo_prediction():
    """
    TODO: change predictions values from 'prediction_blue' to 'BLUE' to match RTE syntax ?
    """
    from django.utils import timezone

    TODAY = timezone.now().date()

    logger.info("Starting the prediction")
    data = get_all_data()
    data = generate_features(data)
    first_day_of_tempo = (TODAY - pd.DateOffset(month=9, day=1)).tz_localize("Europe/Paris")
    predictor = TempoPredictor(data[first_day_of_tempo:].copy())
    tempo_dummies = predictor.predict()
    our_tempo = pd.from_dummies(tempo_dummies).tz_convert("Europe/Paris").tz_localize(None)
    our_tempo.columns = ["our_tempo"]
    rte_tempo = predictor.data["Type_de_jour_TEMPO"].tz_convert("Europe/Paris").tz_localize(None)
    tempo = pd.concat([rte_tempo, our_tempo], axis=1).dropna(how="all")
    write_pred(tempo)


def schedule_tempo_predictions():
    """Schedule the Tempo prediction task"""
    from django_q.tasks import schedule
    from django_q.models import Schedule

    schedule(
        'visualisations_app.tasks.daily_prediction.run_tempo_prediction',
        name='tempo_predictions',
        schedule_type=Schedule.DAILY,
        repeats=-1  # Repeat forever
    )

if __name__ == "__main__":
    logger.info(f"{TODAY=}")
    run_tempo_prediction()
