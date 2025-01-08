import views
from django.urls import path

urlpatterns = [
    path('', views.Acceuill.as_view(), name='accueil'),
]
