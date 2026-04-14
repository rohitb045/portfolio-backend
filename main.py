from fastapi import FastAPI
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
    allow_origins=["*"],  # later restrict to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ENV VARIABLES
MONGO_URL = os.getenv("MONGO_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

print("MONGO_URL:", MONGO_URL)
print("EMAIL:", EMAIL)

# ✅ MongoDB Connection (safe)
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


# ✅ Email Function (SAFE - won't crash server)
def send_email(data: Lead):
    try:
        print("Connecting to SMTP...")

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()

        print("Logging in...")
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

        print("Sending email...")
        server.send_message(msg)
        server.quit()

        print("Email sent successfully ✅")

    except Exception as e:
        print("EMAIL ERROR ❌:", e)


# ✅ Root route (avoid 404)
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# ✅ Main API
@app.post("/submit")
async def submit(data: Lead):
    try:
        print("Received:", data)

        # ✅ Save to MongoDB
        collection.insert_one(data.dict())
        print("Saved to MongoDB ✅")

        # ✅ Try sending email (won’t crash)
        try:
            send_email(data)
        except Exception as e:
            print("Email failed ❌:", e)

        return {"message": "Saved successfully ✅"}

    except Exception as e:
        print("SERVER ERROR ❌:", e)
        return {"message": "Server error"}