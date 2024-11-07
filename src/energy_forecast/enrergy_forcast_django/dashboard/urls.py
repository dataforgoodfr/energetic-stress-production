from django.urls import path
from .views import accueil

urlpatterns = [
    path('', accueil, name='accueil'),
]
