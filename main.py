from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb+srv://shubham:Shubham@cluster0.l6q3n6r.mongodb.net/?appName=Cluster0")
db = client["portfolio"]
collection = db["leads"]

# Schema
class Lead(BaseModel):
    name: str
    email: str
    mobile: str

# API
@app.post("/submit")
async def submit_data(data: Lead):
    collection.insert_one(data.model_dump())
    return {"message": "Data saved successfully"}