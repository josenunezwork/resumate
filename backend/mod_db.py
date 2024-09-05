import sqlite3
from openai import OpenAI
import asyncio

# Set up your OpenAI client
client = OpenAI(api_key='')

def get_db_connection():
    conn = sqlite3.connect('backend/software_jobs_la.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_summary_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE jobs ADD COLUMN description_summary TEXT")
    conn.commit()
    conn.close()

def get_jobs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, description FROM jobs WHERE description_summary IS NULL")
    return cursor.fetchall()

def generate_summary(description):
    prompt = f"""
    Summarize the following job description in 2-3 sentences:

    {description}

    Summary:
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes job descriptions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

def update_job_summary(conn, job_id, summary):
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET description_summary = ? WHERE id = ?", (summary, job_id))
    conn.commit()

async def process_job(conn, job):
    job_id, description = job['id'], job['description']
    summary = generate_summary(description)
    update_job_summary(conn, job_id, summary)
    print(f"Updated summary for job ID: {job_id}")

async def main():
    add_summary_column()
    conn = get_db_connection()
    jobs = get_jobs(conn)

    tasks = [process_job(conn, job) for job in jobs]
    await asyncio.gather(*tasks)

    conn.close()
    print("Job description summaries generation complete.")

if __name__ == "__main__":
    asyncio.run(main())
