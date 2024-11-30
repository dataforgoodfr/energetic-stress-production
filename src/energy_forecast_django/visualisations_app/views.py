"""
    On defini ici les fonctions qui vont etre associé aux urls de l'application.
    Celles-ci peuvent prendre en entré les Requètes d'un Form ou autre pour traiter les données entrée.
    Elles servent egalement a créer les Réponses que l'on visualise avec les templates html generer par les Form ou
    défini par nous.

    Voir https://docs.djangoproject.com/en/5.1/topics/http/views/
"""
import locale
import logging
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.conf import settings
# from energy_forecast import ROOT_DIR

logger = logging.getLogger(__name__)
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    logger.warning("Could not set locale to fr_FR.UTF-8")

gold_dir = ROOT_DIR / "data" / "gold"
tempo_prediction_file = gold_dir / "our_tempo_prediction.csv"

background_colors = {
    "Blanc": "white",
    "Rouge": "red",
    "Bleu": "blue",
    "Inconnu": "silver",
}
text_colors = {
    "Blanc": "black",
    "Rouge": "white",
    "Bleu": "white",
}

map_rte_signal_to_text = {
    "WHITE": "Blanc",
    "RED": "Rouge",
    "BLUE": "Bleu",
    np.nan: "Inconnu",
}
map_our_signal_to_text = {
    "WHITE": "Blanc",
    "RED": "Rouge",
    "BLUE": "Bleu",
    np.nan: "Non calculée",
}

def apply_background_color(val):
    color = background_colors.get(val, "white")
    return f'background-color: {color}; color: {text_colors.get(val, "black")}'

# def accueil(request):
#     today = pd.Timestamp.now().floor("D")
#     predictions = pd.read_csv(tempo_prediction_file, index_col=0, parse_dates=True)[today:]
#     predictions.index = pd.to_datetime(predictions.index, utc=True)
#
#     table_data = {
#         "Date": predictions.index.strftime("%a %d %B %Y"),
#         "Notre prévision à J-1": [map_our_signal_to_text[pred] for pred in predictions["our_tempo_J-1"]],
#         "Notre prévision à J-2": [map_our_signal_to_text[pred] for pred in predictions["our_tempo_J-2"]],
#         "Notre prévision à J-3": [map_our_signal_to_text[pred] for pred in predictions["our_tempo_J-3"]],
#         "Valeur réelle": [map_rte_signal_to_text[true_val] for true_val in predictions["Type_de_jour_TEMPO"]],
#     }
#
#     table_df = pd.DataFrame(table_data).set_index("Date").T
#     styled_table_df = table_df.style.applymap(apply_background_color).to_html()
#
#     context = {
#         'styled_table_df': styled_table_df,
#     }
#
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         rgpd = request.POST.get('rgpd')
#         if rgpd and email:
#             from energy_forecast.dashboard.emails import store_email
#             store_email(email)
#             context['success'] = "Merci pour votre inscription à notre newsletter."
#         elif rgpd and not email:
#             context['error'] = "Veuillez renseigner votre adresse email."
#         elif email and not rgpd:
#             context['error'] = "Vous devez accepter les conditions pour vous inscrire à la newsletter."
#
#     return render(request, 'dashboard/accueil.html', context)
