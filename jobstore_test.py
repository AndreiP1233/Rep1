import sqlite3
import pickle

conn = sqlite3.connect('jobs.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT id, job_state FROM apscheduler_jobs')
jobs = cursor.fetchall()

for id, job_state in jobs:
    try:
        state = pickle.loads(job_state)
        print(f'Job ID: {id}, State:{state}')
    except Exception as e:
        print(f'Ошибка десериализации для Job ID: {id}: {e}')