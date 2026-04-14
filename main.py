from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ENV VARIABLES
MONGO_URL = os.getenv("MONGO_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# ✅ MongoDB
client = MongoClient(MONGO_URL)
db = client["portfolio"]
collection = db["leads"]

# ✅ Schema
class Lead(BaseModel):
    name: str
    email: str
    mobile: str

# ✅ Email function (SAFE)
def send_email(data: Lead):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        msg = MIMEText(f"""
New Lead 🚀

Name: {data.name}
Email: {data.email}
Mobile: {data.mobile}
""")

        msg["Subject"] = "New Portfolio Lead"
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        server.send_message(msg)
        server.quit()

        print("Email sent ✅")

    except Exception as e:
        print("EMAIL ERROR ❌:", e)

# ✅ API (FAST)
@app.post("/submit")
async def submit_data(data: Lead, background_tasks: BackgroundTasks):
    try:
        collection.insert_one(data.model_dump())

        # 🔥 Background email (NO DELAY)
        background_tasks.add_task(send_email, data)

        return {"message": "Saved successfully ✅"}

    except Exception as e:
        print("Error ❌:", e)
        return {"message": "Server error"}