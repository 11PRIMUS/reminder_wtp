from fastapi import FastAPI, Request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import re
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID= os.getenv("PHONE_NUMBER")

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
    
def remind_msg(message, to_number):
    url= f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers={
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"

    }
    data={
        "messaging_product": "whatsapp",
        "to":to_number,
        "type": "text",
        "text": {"body":message}
    }
    resp =requests.post(url, headers=headers, json=data)

