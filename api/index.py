from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from supabase import create_client, Client
import pandas as pd
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 1. Connect to Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_FILE = os.path.join(BASE_DIR, "scenarios.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

MAX_QUOTA = 1000

class SubmitRequest(BaseModel):
    email: str
    delivery_id: str
    policy: str 

@app.get("/task/{email}")
def get_next_task(email: str):
    scenarios_df = pd.read_csv(SCENARIOS_FILE)
    
    # 2. Query the database for this user's completed tasks
    response = supabase.table("annotations").select("delivery_id").eq("email", email).execute()
    annotated_ids = [row["delivery_id"] for row in response.data]
    
    if len(annotated_ids) >= MAX_QUOTA:
        return {"status": "complete", "message": "Quota reached. Thank you!"}

    available_scenarios = scenarios_df[~scenarios_df['delivery_id'].isin(annotated_ids)]

    if available_scenarios.empty:
        return {"status": "complete", "message": "No more scenarios available!"}

    next_task = available_scenarios.iloc[0].fillna("none").to_dict()
    return {"status": "active", "task": next_task, "progress": len(annotated_ids)}

@app.post("/submit")
def submit_annotation(req: SubmitRequest):
    # 3. Insert the new decision safely into the Cloud Database!
    supabase.table("annotations").insert({
        "email": req.email,
        "delivery_id": req.delivery_id,
        "policy": req.policy
    }).execute()
    
    return {"message": "Saved successfully"}

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()