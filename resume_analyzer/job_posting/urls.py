from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.create_job_posting, name='create_job_posting'),
    path('jobs/list/', views.get_job_postings, name='get_job_postings'),
    path('jobs/<uuid:job_id>/', views.get_job_posting_by_id, name='get_job_posting_by_id'),
]