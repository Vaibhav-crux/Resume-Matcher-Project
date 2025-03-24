from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, NotFound
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer, CandidateProfileLiteSerializer  # Import new serializer
from .utils import extract_text_from_file, parse_resume_with_gemini
from resume_analyzer.common.errors import get_error_response
from resume_analyzer import settings
import logging
import requests
import json
import re

# Initialize logger for job posting operations
logger = logging.getLogger('job_posting')

@api_view(['POST'])
def upload_resume(request):
    """
    API to upload and process a resume file.
    Validates file type, extracts text, processes it using Gemini API, and saves the structured data.
    """
    if 'file' not in request.FILES:
        raise ValidationError("No file provided")

    file = request.FILES['file']
    file_name = file.name.lower()
    
    # Determine file type
    if file_name.endswith('.pdf'):
        file_type = 'pdf'
    elif file_name.endswith('.docx'):
        file_type = 'docx'
    elif file_name.endswith('.txt'):
        file_type = 'txt'
    else:
        raise ValidationError("Unsupported file type. Use PDF, DOCX, or TXT")

    try:
        # Extract text from the file
        extracted_text = extract_text_from_file(file, file_type)
        if not extracted_text.strip():
            raise ValidationError("No text could be extracted from the file")

        # Parse the text into structured JSON using Gemini API
        structured_data = parse_resume_with_gemini(extracted_text)

        # Save parsed data to database
        candidate = CandidateProfile(
            extracted_text=extracted_text,
            structured_data=structured_data,
            file_type=file_type
        )
        candidate.save()

        logger.info(f"Resume uploaded and processed successfully: {candidate.id}")
        return Response({"message": "Parsed successfully"}, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        logger.warning(f"Validation error during resume upload: {str(e)}")
        raise
    except (ValueError, requests.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        response, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response, status=status_code)

@api_view(['GET'])
def get_all_resumes(request):
    """
    API to fetch all resume data excluding extracted_text.
    Logs the retrieval process.
    """
    try:
        candidates = CandidateProfile.objects.all()
        serializer = CandidateProfileLiteSerializer(candidates, many=True)
        logger.info(f"Retrieved {len(serializer.data)} resumes")
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching resumes: {str(e)}", exc_info=True)
        response, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response, status=status_code)

@api_view(['GET'])
def sort_candidate_data(request, candidate_id):
    """
    API to sort specific fields from a candidate's structured data using Gemini API.
    Fetches candidate data, sorts skills alphabetically, and updates the record.
    """
    try:
        candidate = CandidateProfile.objects.get(id=candidate_id)
        structured_data = candidate.structured_data

        # Generate sorting prompt for Gemini API
        prompt = f"Given the following list of skills: {structured_data['skills']}, " \
                 "return a sorted list of skills in alphabetical order as a JSON list without any additional text."
        
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Send request to Gemini API for skill sorting
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
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

        # Parse the cleaned JSON string
        sorted_skills = json.loads(json_content)

        # Update structured_data with sorted skills
        structured_data['skills'] = sorted_skills
        candidate.structured_data = structured_data
        candidate.save()

        serializer = CandidateProfileSerializer(candidate)
        logger.info(f"Data sorted for candidate: {candidate_id}")
        return Response(serializer.data)

    except CandidateProfile.DoesNotExist:
        logger.warning(f"Candidate not found: {candidate_id}")
        raise NotFound(f"Candidate with ID {candidate_id} not found")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {str(e)} - Raw response: {raw_text}")
        raise ValueError("Invalid JSON format in Gemini response")
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Error sorting candidate data {candidate_id}: {str(e)}", exc_info=True)
        response, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response, status=status_code)