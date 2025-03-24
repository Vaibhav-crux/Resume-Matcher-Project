from rest_framework import serializers
from .models import CandidateProfile

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['id', 'extracted_text', 'structured_data', 'file_type', 'created_at', 'updated_at']

class CandidateProfileLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['id', 'structured_data', 'file_type', 'created_at', 'updated_at']