# emotion_based/urls.py
from django.urls import path
from .views import recommend_movies_and_music, recommendation_result_view

urlpatterns = [
    path('recommend/', recommend_movies_and_music, name='recommend'),
    path('recommendations/', recommendation_result_view, name='recommend_result'),
]
