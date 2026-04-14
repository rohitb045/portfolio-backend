from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ENV VARIABLES
MONGO_URL = os.getenv("MONGO_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# ✅ MongoDB Connection
if not MONGO_URL:
    raise Exception("MONGO_URL not set ❌")

client = MongoClient(MONGO_URL)
db = client["portfolio"]
collection = db["leads"]

# ✅ Schema
class Lead(BaseModel):
    name: str
    email: str
    mobile: str

# ✅ Email Function (runs in background)
def send_email(data: Lead):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        msg = MIMEText(f"""
New Resume Request 🚀

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

# ✅ Root route
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

# ✅ Main API (FAST RESPONSE)
@app.post("/submit")
async def submit(data: Lead, background_tasks: BackgroundTasks):
    try:
        print("Received:", data)

        # ✅ Save to MongoDB
        collection.insert_one(data.dict())
        print("Saved to MongoDB ✅")

        # ✅ Send email in background (NO DELAY)
        background_tasks.add_task(send_email, data)

        return {"message": "Saved successfully ✅"}

    except Exception as e:
        print("SERVER ERROR ❌:", e)
        return {"message": "Server error"}