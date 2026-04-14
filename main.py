from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rohit-bulbule-portfolio.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
client = MongoClient(os.getenv("MONGO_URL"))
db = client["portfolio"]
collection = db["leads"]

# Your email (CHANGE THIS)
EMAIL = "rohitbulbule07@gmail.com"
PASSWORD = "zyhm qewz dheh upjw"


# Form schema
class Lead(BaseModel):
    name: str
    email: str
    mobile: str


# Function to send email
def send_email(data: Lead):
    msg = MIMEText(
        f"""
New Resume Request:

Name: {data.name}
Email: {data.email}
Mobile: {data.mobile}
"""
    )

    msg["Subject"] = "New Portfolio Lead 🚀"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()


# API
@app.post("/submit")
async def submit(data: Lead):
    collection.insert_one(data.dict())

    # send email
    send_email(data)

    return {"message": "Saved + Email Sent"}
