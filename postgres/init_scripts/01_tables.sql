\c stress_energetic;

CREATE TABLE IF NOT EXISTS eco2mix_raw (
    date_heure TIMESTAMP,
    consommation FLOAT,
    eolien FLOAT,
    solaire FLOAT
);

CREATE TABLE IF NOT EXISTS pred_conso_rte (
    date_heure TIMESTAMP,
    consommation FLOAT
);

CREATE TABLE IF NOT EXISTS forecast_flux_solaire (
    date_heure TIMESTAMP,
    departement CHAR,
    delta_hours_pred FLOAT,
    flux_solaire FLOAT
);

CREATE TABLE IF NOT EXISTS forecast_vent (
    date_heure TIMESTAMP,
    departement CHAR,
    delta_hours_pred FLOAT,
    vent FLOAT
);

CREATE TABLE IF NOT EXISTS forecast_ENR (
    date_heure TIMESTAMP,
    delta_hours_pred FLOAT,
    eolien FLOAT,
    solaire FLOAT
);

-- Je ne pense pas que ça soit nécessaire, l'information est gardée indirectement
-- dans les données pour prédire le jour tempo
-- CREATE TABLE IF NOT EXISTS temperature (
--     date_heure TIMESTAMP,
--     temperature FLOAT
-- );

CREATE TABLE IF NOT EXISTS prep_prediction_tempo (
    date DATE,
    consommation FLOAT,
    eolien FLOAT,
    solaire FLOAT,
    temperature FLOAT,
    production_nette FLOAT,
    production_nette_q40 FLOAT,
    production_nette_q80 FLOAT,
    mean_temp_q30 FLOAT,
    jour_tempo CHAR,
);

CREATE TABLE IF NOT EXISTS prediction_tempo (
    date DATE,
    delta_hours_pred FLOAT,
    eolien FLOAT,
    solaire FLOAT
);
