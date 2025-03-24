# Resume Matcher Project

## Overview  
The **Resume Matcher Project** is a web application that allows users to post job listings, upload resumes, and match resumes to jobs using AI-powered scoring. It consists of a Django backend for API services and a Streamlit frontend for an interactive user interface. The project is containerized using Docker and Docker Compose for easy deployment.

### Features  
- **Job Posting**: Create and view job postings with required skills  
- **Resume Upload**: Upload resumes (PDF, DOCX, TXT) and parse them into structured data  
- **Resume Matching**: Calculate a matching score and summary between a job and a resume using the AI API  
- **Match Viewing**: View all matches with filtering by job title and color-coded indicators (Red/Yellow/Green)  
- **Dockerized**: Run the backend and frontend in containers for consistency across environments  

---

## Project Structure  
```
eduBild/
├── .env.example              # Example environment variables file
├── .gitignore                # Git ignore file
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile.django         # Dockerfile for Django backend
├── Dockerfile.streamlit      # Dockerfile for Streamlit frontend
├── README.md                 # Project documentation
├── requirements.txt          # Project-wide Python dependencies
├── resume_analyzer/          # Django project directory
│   ├── db.sqlite3            # SQLite database file
│   ├── manage.py             # Django management script
│   ├── candidates_resume/    # App for resume upload and parsing
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   ├── views.py
│   │   ├── __init__.py
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── __init__.py
│   ├── job_posting/          # App for job posting management
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── __init__.py
│   │   └── migrations/
│   │       ├── 0001_initial.py
│   │       └── __init__.py
│   ├── logs/                 # Log files directory
│   │   ├── candidates_resume.log
│   │   └── job_posting.log
│   ├── media/                # Uploaded media files
│   │   └── resumes/
│   │       ├── Vishesh_148Z.pdf
│   │       ├── Vishesh_148Z_DOdZ0pF.pdf
│   │       ├── Vishesh_148Z_GFn4SxV.pdf
│   │       └── Vishesh_148Z_uBasG6x.pdf
│   ├── resume_analyzer/      # Django settings and configuration
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── __init__.py
│   │   └── common/
│   │       └── errors.py
│   └── resume_matcher/       # App for resume-job matching
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       ├── __init__.py
│       └── migrations/
│           ├── 0001_initial.py
│           ├── 0002_resumematchscore_summary.py
│           └── __init__.py
├── streamlit_app/            # Streamlit frontend directory
│   └── app.py                # Main Streamlit script
└── test/                     # Test directory (optional)
    └── sqll.py
```

---
## Demo
Google Drive Link: `https://drive.google.com/file/d/1TfBuDmxAbm5vnTYFWZ4TX96Yk6FMm-b1/view?usp=drive_link`

---

## Prerequisites  
- **Docker**: Install Docker and Docker Compose (included with Docker Desktop on Windows/Mac)  
- **Python**: Version 3.11+ (for local development without Docker)  
- **Git**: To clone the repository  

---

## Setup Instructions  

### 1. Clone the Repository  
```bash
git clone git remote add origin https://github.com/Vaibhav-crux/Resume-Matcher-Project.git
cd Resume-Matcher-Project
```

### 2. Configure Environment Variables  
Copy `.env.example` to `.env` and update the values:  
```bash
cp .env.example .env
```
Edit `.env`:  
```
AI_API_KEY=your_actual_AI_api_key_here
BASE_URL=http://django:8000/api/  # For Docker; use http://127.0.0.1:8000/api/ for local dev
```

### 3. Using Docker (Recommended)  
#### Build and Run  
```bash
docker-compose up --build
```
- Django: Accessible at `http://localhost:8000`  
- Streamlit: Accessible at `http://localhost:8501`  

#### Stop Services  
```bash
docker-compose down
```

#### To Reset the Database  
```bash
docker-compose down -v
```

### 4. Local Development (Without Docker)  
#### Install Dependencies  
```bash
pip install -r requirements.txt
cd streamlit_app
pip install -r requirements.txt
```

#### Run Django  
```bash
cd resume_analyzer
python manage.py migrate
python manage.py runserver
```

#### Run Streamlit  
In a separate terminal:  
```bash
cd streamlit_app
streamlit run app.py
```

---

## Usage  

### Streamlit Interface  
Open `http://localhost:8501` in your browser to access the Streamlit dashboard. Use the tabs to:  
- **Post Job**: Enter job details and submit  
- **View Jobs**: Fetch and display all job postings  
- **Upload Resume**: Upload a resume file (PDF, DOCX, TXT)  
- **View Resumes**: List all parsed resumes  
- **Match Resume**: Enter Job ID and Candidate ID to calculate a match score  
- **View Matches**: Filter matches by job title and view scores with color indicators (🟢 Green: ≥70%, 🟡 Yellow: ≥40%, 🔴 Red: <40%)  

### API Endpoints  

#### Job Posting APIs  
##### `POST /api/jobs/` - Create a Job Posting  
**Request:**  
```bash
curl -X POST http://localhost:8000/api/jobs/ \
-H "Content-Type: application/json" \
-d '{
      "title": "Software Engineer",
      "company": "Tech Corp",
      "required_skills": ["Python", "Django"]
    }'
```
**Response (201 Created):**  
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Software Engineer",
  "company": "Tech Corp",
  "required_skills": ["Python", "Django"],
  "created_at": "2025-03-24T10:00:00Z",
  "updated_at": "2025-03-24T10:00:00Z"
}
```

##### `GET /api/jobs/list/` - List All Jobs  
**Request:**  
```bash
curl -X GET http://localhost:8000/api/jobs/list/
```
**Response (200 OK):**  
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "required_skills": ["Python", "Django"],
    "created_at": "2025-03-24T10:00:00Z",
    "updated_at": "2025-03-24T10:00:00Z"
  }
]
```

#### Resume Management APIs  
##### `POST /api/resume/upload/` - Upload a Resume  
**Request:**  
```bash
curl -X POST http://localhost:8000/api/resume/upload/ \
-F "file=@/path/to/resume.pdf"
```
**Response (201 Created):**  
```json
{
  "message": "Parsed successfully"
}
```

##### `GET /api/resume/all/` - List All Resumes  
**Request:**  
```bash
curl -X GET http://localhost:8000/api/resume/all/
```
**Response (200 OK):**  
```json
[
  {
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2g3h4i5j",
    "structured_data": {
      "name": "John Doe",
      "skills": ["Python", "Django"],
      "education": ["BS Computer Science"],
      "work_experience": ["Software Engineer at Tech Corp"]
    },
    "file_type": "pdf",
    "created_at": "2025-03-24T14:00:00Z",
    "updated_at": "2025-03-24T14:00:00Z"
  }
]
```

#### Matching APIs  
##### `GET /api/match/<job_id>/<candidate_id>/` - Calculate Matching Score  
**Request:**  
```bash
curl -X GET http://localhost:8000/api/match/550e8400-e29b-41d4-a716-446655440000/a1b2c3d4-e5f6-4a7b-8c9d-0e1f2g3h4i5j/
```
**Response (200 OK):**  
```json
{
  "id": "b2c3d4e5-f6g7-4h8i-9j0k-1l2m3n4o5p6",
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_profile_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2g3h4i5j",
  "matching_score": 85.5,
  "summary": "The candidate's skills in Python and Django align well with the job's requirements...",
  "created_at": "2025-03-24T16:00:00Z",
  "updated_at": "2025-03-24T16:00:00Z"
}
```

---

## Development Notes  
- **Database**: Uses SQLite (`db.sqlite3`) for simplicity. For production, consider switching to PostgreSQL  
- **Logging**: Logs are stored in `logs/`
- **Media**: Uploaded resumes are stored in `media/resumes/`  
- **AI API**: Requires a valid `AI_API_KEY` for resume parsing and matching  

