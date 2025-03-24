from django.db import models
import uuid
from job_posting.models import JobPosting
from candidates_resume.models import CandidateProfile

class ResumeMatchScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='matches')
    candidate_profile = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='matches')
    matching_score = models.FloatField()
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job_posting', 'candidate_profile')
        indexes = [
            models.Index(fields=['job_posting', 'candidate_profile']),
        ]
        ordering = ['-matching_score']

    def __str__(self):
        return f"Match: {self.job_posting.title} - {self.candidate_profile.id} ({self.matching_score}%)"