from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('emotion_recommendation.recommendation.emotion_based.urls')),
    path('feedback/', include('emotion_recommendation.recommendation.feedback.urls')),
]