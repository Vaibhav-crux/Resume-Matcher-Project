from django.urls import path
from . import views

urlpatterns = [
    path('resume/upload/', views.upload_resume, name='upload_resume'),
    path('resume/all/', views.get_all_resumes, name='get_all_resumes'),
    path('resume/<uuid:candidate_id>/sort/', views.sort_candidate_data, name='sort_candidate_data'),
]