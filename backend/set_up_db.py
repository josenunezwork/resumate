import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timedelta
import ssl
import certifi
import json

# API Key and Endpoints
API_KEY= ''
SEARCH_ENDPOINT = 'https://api.coresignal.com/cdapi/v1/linkedin/job/search/filter'
COLLECT_ENDPOINT = 'https://api.coresignal.com/cdapi/v1/linkedin/job/collect/'

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

async def fetch_jobs(session, keyword, location, last_updated):
    url = SEARCH_ENDPOINT
    payload = {
        'keyword_description': keyword,  # Changed from 'title' to 'keyword_description'
        'location': location,
        'application_active': True,
        'last_updated_gte': last_updated.strftime("%Y-%m-%d %H:%M:%S")  # Format date as string
    }
    
    try:
        async with session.post(url, headers=headers, json=payload, ssl=ssl.create_default_context(cafile=certifi.where())) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"Error in search: {response.status}")
                print(f"Error details: {error_text}")
                print(f"Request payload: {json.dumps(payload, indent=2)}")
                return None
    except Exception as e:
        print(f"Error fetching jobs: {str(e)}")
        return None

async def collect_job_details(session, job_id):
    url = f"{COLLECT_ENDPOINT}{job_id}"
    
    try:
        async with session.get(url, headers=headers, ssl=ssl.create_default_context(cafile=certifi.where())) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"Error in collect: {response.status}")
                print(f"Error details: {error_text}")
                return None
    except Exception as e:
        print(f"Error collecting job details: {str(e)}")
        return None

def setup_database():
    conn = sqlite3.connect('backend/software_jobs_la.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY,
                  title TEXT,
                  company TEXT,
                  location TEXT,
                  description TEXT,
                  application_url TEXT,
                  date_posted TEXT)''')
    conn.commit()
    return conn

def insert_job(conn, job):
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO jobs
                 (id, title, company, location, description, application_url, date_posted)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (job.get('id'),
               job.get('title'),
               job.get('company_name'),
               job.get('location'),
               job.get('description'),
               job.get('application_url', ''),
               job.get('created_at', '')))
    conn.commit()

async def process_keyword_location(session, conn, keyword, location, last_updated):
    jobs = await fetch_jobs(session, keyword, location, last_updated)
    
    if jobs:
        for job_id in jobs[:10]:  # Limit to 10 jobs for demonstration
            job_details = await collect_job_details(session, job_id)
            if job_details:
                insert_job(conn, job_details)
                print(f"Inserted job: {job_details.get('title', 'Unknown')} at {job_details.get('company_name', 'Unknown')}")

async def main():
    conn = setup_database()
    
    keywords = ["software engineer", "data scientist", "product manager"]
    locations = ["Los Angeles, CA", "San Francisco, CA", "New York, NY"]
    last_updated = datetime.now() - timedelta(days=30)  # Jobs updated in the last 30 days
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_keyword_location(session, conn, keyword, location, last_updated) 
                 for keyword in keywords 
                 for location in locations]
        await asyncio.gather(*tasks)
    
    conn.close()
    print("Database population complete.")

if __name__ == "__main__":
    asyncio.run(main())