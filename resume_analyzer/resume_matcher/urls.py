from django.urls import path
from . import views

urlpatterns = [
    path('match/<uuid:job_id>/<uuid:candidate_id>/', views.get_matching_score, name='get_matching_score'),
    path('match/all/', views.get_all_matches, name='get_all_matches'),
]