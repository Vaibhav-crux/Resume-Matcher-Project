import pdfplumber
import docx2txt
import logging
import requests
import json
import re
from resume_analyzer import settings

# Initialize logger for job posting operations
logger = logging.getLogger('job_posting')

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def extract_text_from_file(file, file_type):
    """
    Extract text from a given file based on its type.
    Supports PDF, DOCX, and TXT formats.
    """
    try:
        if file_type == 'pdf':
            with pdfplumber.open(file) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            return text
        elif file_type == 'docx':
            return docx2txt.process(file)
        elif file_type == 'txt':
            return file.read().decode('utf-8')
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}", exc_info=True)
        raise

def parse_resume_with_gemini(text):
    """
    Use the Gemini API to parse resume text into structured JSON.
    Extracts key fields like name, skills, education, and work experience.
    """
    try:
        prompt = (
            "Parse the following resume text into structured JSON with the following fields: "
            "name (string), skills (list of strings), education (list of strings), "
            "work_experience (list of strings). Return only the JSON object without any additional text. "
            "Here is the text:\n\n" + text
        )
        
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Send request to Gemini API for parsing
        response = requests.post(
            f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logger.error(f"Gemini API call failed: {response.text}")
            raise Exception("Failed to parse resume with Gemini API")

        gemini_response = response.json()
        raw_text = gemini_response['candidates'][0]['content']['parts'][0]['text']

        json_content = re.sub(r'```json\s*|\s*```', '', raw_text).strip()

        # Parse the cleaned JSON string into a Python dictionary
        structured_data = json.loads(json_content)
        return structured_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {str(e)} - Raw response: {raw_text}")
        raise Exception("Invalid JSON format in Gemini response")
    except Exception as e:
        logger.error(f"Error parsing resume with Gemini: {str(e)}", exc_info=True)
        raise
