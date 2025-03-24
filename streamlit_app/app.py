# streamlit_app/app.py
import streamlit as st
import requests
from decouple import config  

# Base URL for Django API (adjust if running on a different host/port)
BASE_URL = config('BASE_URL')

# Streamlit app
st.title("Resume Matcher Dashboard")

# Tabs for different functionalities
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Post Job", "View Jobs", "Upload Resume", "View Resumes", "Match Resume", "View Matches"
])

# Tab 1: Post Job
with tab1:
    st.header("Post a Job")
    job_title = st.text_input("Job Title")
    company = st.text_input("Company")
    skills = st.text_input("Required Skills (comma-separated, e.g., Python, Django)")
    
    if st.button("Submit Job"):
        if job_title and company and skills:
            payload = {
                "title": job_title,
                "company": company,
                "required_skills": skills.split(", ")
            }
            response = requests.post(f"{BASE_URL}jobs/", json=payload)
            if response.status_code == 201:
                st.success("Job posted successfully!")
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("Please fill in all fields.")

# Tab 2: View Jobs
with tab2:
    st.header("View All Jobs")
    if st.button("Fetch Jobs"):
        response = requests.get(f"{BASE_URL}jobs/list/")
        if response.status_code == 200:
            jobs = response.json()
            for job in jobs:
                st.write(f"**ID: {job['id']}**")
                st.write(f"**{job['title']}** - {job['company']}")
                st.write(f"Skills: {', '.join(job['required_skills'])}")
                st.write("---")
        else:
            st.error(f"Error: {response.text}")

# Tab 3: Upload Resume
with tab3:
    st.header("Upload Resume")
    resume_file = st.file_uploader("Choose a resume file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    
    if st.button("Upload Resume"):
        if resume_file:
            files = {"file": (resume_file.name, resume_file, resume_file.type)}
            response = requests.post(f"{BASE_URL}resume/upload/", files=files)
            if response.status_code == 201:
                st.success("Parsed successfully!")
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("Please upload a file.")

# Tab 4: View Resumes
with tab4:
    st.header("View All Resumes")
    if st.button("Fetch Resumes"):
        response = requests.get(f"{BASE_URL}resume/all/")
        if response.status_code == 200:
            resumes = response.json()
            for resume in resumes:
                st.write(f"**Candidate ID**: {resume['id']}")
                st.write(f"Name: {resume['structured_data']['name']}")
                st.write(f"Skills: {', '.join(resume['structured_data']['skills'])}")
                st.write(f"Education: {', '.join(resume['structured_data']['education'])}")
                st.write(f"Work Experience: {', '.join(resume['structured_data']['work_experience'])}")
                st.write(f"File Type: {resume['file_type']}")
                st.write("---")
        else:
            st.error(f"Error: {response.text}")

# Tab 5: Match Resume
with tab5:
    st.header("Match Resume with Job")
    job_id = st.text_input("Job ID (UUID)")
    candidate_id = st.text_input("Candidate ID (UUID)")
    
    if st.button("Calculate Match"):
        if job_id and candidate_id:
            response = requests.get(f"{BASE_URL}match/{job_id}/{candidate_id}/")
            if response.status_code == 200:
                match = response.json()
                st.write(f"**Matching Score**: {match['matching_score']}%")
                st.write(f"**Summary**: {match['summary']}")
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("Please provide both Job ID and Candidate ID.")

# Tab 6: View Matches
with tab6:
    st.header("View All Matches")

    # Fetch all job titles for the filter
    job_response = requests.get(f"{BASE_URL}jobs/list/")
    job_titles = ["All Jobs"]  # Default option to show all matches
    job_title_to_id = {"All Jobs": None}  # Mapping for filtering
    
    if job_response.status_code == 200:
        jobs = job_response.json()
        for job in jobs:
            job_titles.append(job['title'])
            job_title_to_id[job['title']] = job['id']
    else:
        st.error("Failed to fetch job titles for filtering.")

    # Filter dropdown
    selected_job_title = st.selectbox("Filter by Job Title", job_titles)

    if st.button("Fetch Matches"):
        response = requests.get(f"{BASE_URL}match/all/")
        if response.status_code == 200:
            matches = response.json()
            
            # Filter matches based on selected job title
            if selected_job_title != "All Jobs":
                job_id = job_title_to_id[selected_job_title]
                matches = [match for match in matches if match['job_posting']['id'] == str(job_id)]
            
            if not matches:
                st.write("No matches found for the selected job.")
            else:
                for match in matches:
                    # Determine indicator color based on matching score
                    score = match['matching_score']
                    if score >= 70:
                        indicator_color = "🟢"  # Green
                    elif score >= 40:
                        indicator_color = "🟡"  # Yellow
                    else:
                        indicator_color = "🔴"  # Red

                    st.write(f"**Match ID**: {match['id']} {indicator_color}")
                    st.write(f"**Job**: {match['job_posting']['title']} ({match['job_posting']['company']})")
                    st.write(f"Job Skills: {', '.join(match['job_posting']['required_skills'])}")
                    st.write(f"**Candidate**: {match['candidate_profile']['structured_data']['name']}")
                    st.write(f"Candidate Skills: {', '.join(match['candidate_profile']['structured_data']['skills'])}")
                    st.write(f"Matching Score: {score}%")
                    st.write(f"Summary: {match['summary']}")
                    st.write("---")
        else:
            st.error(f"Error: {response.text}")