import sqlite3
from openai import OpenAI
import re
import os
import json
from datetime import datetime

# Set up your OpenAI client
client = OpenAI(api_key='enter your own')

def get_db_connection():
    conn = sqlite3.connect('software_jobs_la.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_jobs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    return cursor.fetchall()

def generate_resume(job_title, job_description, applicant_context):
    prompt = f"""
    Create a tailored, professional resume for the following job using Markdown formatting:

    Job Title: {job_title}
    Job Description: {job_description}

    Applicant Information:
    {applicant_context}

    Generate a professional resume that highlights the applicant's relevant skills and experience for this specific job.
    Use the following Markdown structure:

    <div align="center">

    # [Applicant Name]

    [Email] | [Phone] | [Location] | [LinkedIn]

    ## Summary

    [A brief, impactful summary of the applicant's qualifications]

    ## Skills

    - [Skill 1]
    - [Skill 2]
    - [Skill 3]
    ...

    ## Experience

    ### [Job Title] at [Company]
    [Employment Period]

    - [Achievement/Responsibility 1]
    - [Achievement/Responsibility 2]
    - [Achievement/Responsibility 3]
    ...

    ### [Previous Job Title] at [Previous Company]
    [Employment Period]

    - [Achievement/Responsibility 1]
    - [Achievement/Responsibility 2]
    - [Achievement/Responsibility 3]
    ...

    ## Education

    ### [Degree] in [Field of Study]
    [University Name] - [Graduation Year]

    ## Certifications

    - [Certification 1]
    - [Certification 2]
    ...

    </div>
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional resume writer skilled in Markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

def sanitize_filename(filename):
    # Remove or replace characters that are problematic in filenames
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    return filename

def save_resume(resume, job_title, company):
    # Sanitize job title and company name
    safe_job_title = sanitize_filename(job_title)
    safe_company = sanitize_filename(company)
    
    # Create a directory for resumes if it doesn't exist
    resume_dir = 'generated_resumes'
    os.makedirs(resume_dir, exist_ok=True)
    
    # Create filename
    filename = f"resume_{safe_job_title}_{safe_company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(resume_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resume)
    print(f"Resume saved as {filepath}")


def main():
    conn = get_db_connection()
    jobs = get_jobs(conn)

    # Sample applicant context - you can modify this or load it from a file
    applicant_context = """
    Name: Alex Johnson
    Education: Bachelor's in Computer Science from UCLA
    Years of Experience: 5
    Skills: Python, JavaScript, React, Node.js, SQL, Git
    Previous Roles: Software Engineer at TechCorp, Junior Developer at StartupX
    Achievements: Led a team of 3 to develop a high-traffic web application, Increased code efficiency by 30% in previous role
    """

    for job in jobs:
        print(f"Generating resume for {job['title']} at {job['company']}")
        resume = generate_resume(job['title'], job['description'], applicant_context)
        save_resume(resume, job['title'], job['company'])

    conn.close()
    print("Resume generation complete.")

if __name__ == "__main__":
    main()
