from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from .models import ResumeMatchScore
from .serializers import ResumeMatchScoreSerializer, ResumeMatchScoreDetailSerializer
from job_posting.models import JobPosting
from candidates_resume.models import CandidateProfile
from resume_analyzer.common.errors import get_error_response
from resume_analyzer import settings
import logging
import requests
import json
import re

# Initialize logger for job posting operations
logger = logging.getLogger('job_posting')

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@api_view(['GET'])
def get_matching_score(request, job_id, candidate_id):
    """
    API to fetch or calculate the matching score and summary between a job posting and a resume.
    If a cached score exists, it is returned; otherwise, it is calculated using Gemini API.
    """
    try:
        # Fetch job posting and candidate profile
        job_posting = JobPosting.objects.get(id=job_id)
        candidate_profile = CandidateProfile.objects.get(id=candidate_id)

        # Check if a match score already exists in the database
        try:
            match = ResumeMatchScore.objects.get(job_posting=job_posting, candidate_profile=candidate_profile)
            serializer = ResumeMatchScoreSerializer(match)
            logger.info(f"Retrieved cached matching score for job {job_id} and candidate {candidate_id}")
            return Response(serializer.data)
        except ResumeMatchScore.DoesNotExist:
            pass  # No cached score, proceed with calculation

        # Prepare data for Gemini API request
        job_data = {
            "title": job_posting.title,
            "company": job_posting.company,
            "required_skills": job_posting.required_skills
        }
        resume_data = candidate_profile.structured_data

        # Construct prompt for AI-based scoring and summary generation
        prompt = (
            f"Calculate a matching score (0-100) between the following job posting and resume. "
            f"Also provide a brief summary (2-3 sentences) explaining how well the resume matches the job criteria, "
            f"considering skills overlap, education relevance, and work experience alignment. "
            f"Return a JSON object with 'score' (float) and 'summary' (string) fields, without additional text.\n\n"
            f"Job Posting: {json.dumps(job_data)}\n\n"
            f"Resume: {json.dumps(resume_data)}"
        )

        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Call Gemini API for score calculation
        response = requests.post(
            f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logger.error(f"Gemini API call failed: {response.text}")
            raise requests.RequestException("Failed to call Gemini API")

        gemini_response = response.json()
        raw_text = gemini_response['candidates'][0]['content']['parts'][0]['text']

        # Remove Markdown code blocks if present
        json_content = re.sub(r'```json\s*|\s*```', '', raw_text).strip()

        # Parse JSON to extract score and summary
        result = json.loads(json_content)
        score = float(result['score'])
        summary = result['summary']

        # Save the score and summary to the database
        match = ResumeMatchScore(
            job_posting=job_posting,
            candidate_profile=candidate_profile,
            matching_score=score,
            summary=summary
        )
        match.save()

        serializer = ResumeMatchScoreSerializer(match)
        logger.info(f"Calculated and saved matching score {score} for job {job_id} and candidate {candidate_id}")
        return Response(serializer.data)

    except JobPosting.DoesNotExist:
        logger.warning(f"Job posting not found: {job_id}")
        raise NotFound(f"Job posting with ID {job_id} not found")
    except CandidateProfile.DoesNotExist:
        logger.warning(f"Candidate profile not found: {candidate_id}")
        raise NotFound(f"Candidate profile with ID {candidate_id} not found")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {str(e)} - Raw response: {raw_text}")
        raise ValueError("Invalid JSON format in Gemini response")
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error(f"Error calculating matching score for job {job_id} and candidate {candidate_id}: {str(e)}", exc_info=True)
        response, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response, status=status_code)

@api_view(['GET'])
def get_all_matches(request):
    """
    API to fetch all matching scores along with job and candidate details.
    """
    try:
        matches = ResumeMatchScore.objects.all()
        serializer = ResumeMatchScoreDetailSerializer(matches, many=True)
        logger.info(f"Retrieved {len(serializer.data)} matches")
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching all matches: {str(e)}", exc_info=True)
        response, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response, status=status_code)
