from fastapi import FastAPI, Request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from fastapi.responses import PlainTextResponse
import re
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID= os.getenv("PHONE_NUMBER")
VERIFY_TOKEN= os.getenv("VERIFY_TOKEN")

app=FastAPI()
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.start()

def parse_msg(text):
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
        now=datetime.now()
        reminder_time=now.replace(hour=exam_time.hour, minute=exam_time.minute,second=0, microsecond=0)
        if reminder_time <now:
            reminder_time += timedelta(days=1)
        return reminder_time
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

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    data = await request.json()
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", [])
                messages = value.get("messages", [])
                for msg in messages:
                    from_number = msg["from"]
                    text= msg["text"]["body"]
                    reminder_time= parse_msg(text)
                    if reminder_time:
                        scheduler.add_job(remind_msg, 'date', run_date=reminder_time, args=[f"REMINDER: {text}", from_number])
                        remind_msg(f"REMINDER set for: {reminder_time.strftime('%d %b, %Y at %I:%M %p')}",from_number)

                    else:
                        remind_msg("failed getting time",from_number)
    
    return "ok"

@app.get("/webhook",response_class=PlainTextResponse)
async def verify(
    hub_mode: str = "", hub_verify_token: str = "", hub_challenge: str = ""
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    return "Verification failed"