from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# ✅ CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB (from ENV)
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["portfolio"]
collection = db["leads"]

# ✅ Email ENV
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


# ✅ Schema
class Lead(BaseModel):
    name: str
    email: str
    mobile: str


# ✅ Send Email Function
def send_email(data: Lead):
    try:
        msg = MIMEText(f"""
New Resume Request 🚀

Name: {data.name}
Email: {data.email}
Mobile: {data.mobile}
""")

        msg["Subject"] = "New Portfolio Lead"
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("Email sent successfully ✅")

    except Exception as e:
        print("Email error ❌:", e)


# ✅ API Route
@app.post("/submit")
async def submit(data: Lead):
    try:
        # Save to MongoDB
        collection.insert_one(data.dict())

        # Send Email
        send_email(data)

        return {"message": "Saved + Email Sent ✅"}

    except Exception as e:
        print("Error ❌:", e)
        return {"message": "Error saving data"}