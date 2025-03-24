from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, NotFound
from .models import JobPosting
from .serializers import JobPostingSerializer
import logging

# Initialize logger for job posting operations
logger = logging.getLogger('job_posting')

@api_view(['POST'])
def create_job_posting(request):
    """
    Create a new job posting.
    Validates and saves the job posting data from the request.
    Logs the creation process and raises a ValidationError if invalid.
    """
    serializer = JobPostingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"New job posting created: {serializer.data['title']} at {serializer.data['company']}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Failed to create job posting: {serializer.errors}")
    raise ValidationError(serializer.errors)  # Raise exception instead of returning Response

@api_view(['GET'])
def get_job_postings(request):
    """
    Retrieve all job postings with optional filters for title and company.
    Logs the number of retrieved postings.
    """
    title = request.query_params.get('title', None)
    company = request.query_params.get('company', None)
    
    queryset = JobPosting.objects.all()
    if title:
        queryset = queryset.filter(title__icontains=title)  # Filter by title (case insensitive)
    if company:
        queryset = queryset.filter(company__icontains=company)  # Filter by company (case insensitive)
    
    serializer = JobPostingSerializer(queryset, many=True)
    logger.info(f"Retrieved {len(serializer.data)} job postings with filters - title: {title}, company: {company}")
    return Response(serializer.data)

@api_view(['GET'])
def get_job_posting_by_id(request, job_id):
    """
    Retrieve a specific job posting by its ID.
    Logs retrieval success or failure.
    """
    try:
        job = JobPosting.objects.get(id=job_id)  # Fetch job by ID
        serializer = JobPostingSerializer(job)
        logger.info(f"Retrieved job posting: {job_id}")
        return Response(serializer.data)
    except JobPosting.DoesNotExist:
        logger.warning(f"Job posting not found: {job_id}")
        raise NotFound(f"Job posting with ID {job_id} not found")
