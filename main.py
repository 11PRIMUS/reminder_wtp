from fastapi import FastAPI, Request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import re


app=FastAPI()
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.start()

def msg(text):
    pattern = r"(?i) (test|exam) [^\d]*(\d{1,2}(?::\d{2})?)\s*([ap]m)?"
    match = re.search(pattern, text)

    if match:
        time_part=match.group(2)
        ampm = match.group(3) or ''
        try:
            if ':' in time_part:
                exam_time = datetime.strptime(f"{time_part} {ampm}", "%I:%M %p" if ampm else "%H:%M")
            
            else:
                exam_time = datetime.strptime(f"{time_part} {ampm}", "%I %p" if ampm else "%H")
        except Exception:
            return None
    
        