from rest_framework import serializers
from .models import ResumeMatchScore
from job_posting.serializers import JobPostingSerializer
from candidates_resume.serializers import CandidateProfileLiteSerializer

class ResumeMatchScoreSerializer(serializers.ModelSerializer):
    job_posting_id = serializers.UUIDField(source='job_posting.id')
    candidate_profile_id = serializers.UUIDField(source='candidate_profile.id')

    class Meta:
        model = ResumeMatchScore
        fields = ['id', 'job_posting_id', 'candidate_profile_id', 'matching_score', 'summary', 'created_at', 'updated_at']

class ResumeMatchScoreDetailSerializer(serializers.ModelSerializer):
    job_posting = JobPostingSerializer()  # Job details
    candidate_profile = CandidateProfileLiteSerializer()  # Candidate details

    class Meta:
        model = ResumeMatchScore
        fields = ['id', 'job_posting', 'candidate_profile', 'matching_score', 'summary', 'created_at', 'updated_at']