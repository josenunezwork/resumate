from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import sqlite3
import os
from datetime import datetime
from openai_api import generate_resume, get_db_connection, get_jobs, save_resume

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')

# Set up your OpenAI client
client = OpenAI(api_key='your_api_key_here')

def get_db_connection():
    conn = sqlite3.connect('backend/software_jobs_la.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume_route():
    data = request.json
    job_title = data.get('job_title')
    job_description = data.get('job_description')
    applicant_context = data.get('applicant_context')
    
    resume = generate_resume(job_title, job_description, applicant_context)
    return jsonify({'resume': resume, 'markdown': resume})

@app.route('/jobs')
def get_all_jobs():
    conn = get_db_connection()
    jobs = get_jobs(conn)
    conn.close()
    return jsonify([dict(job) for job in jobs])

def save_resume(resume, job_title, company):
    resume_dir = 'backend/generated_resumes'
    os.makedirs(resume_dir, exist_ok=True)
    
    filename = f"resume_{job_title.replace(' ', '_')}_{company.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(resume_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resume)
