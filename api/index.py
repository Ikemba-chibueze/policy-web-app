from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Fix paths for Vercel's serverless environment
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
    # Vercel CAN read the scenarios CSV without issues
    scenarios_df = pd.read_csv(SCENARIOS_FILE)
    
    # TODO: Fetch user annotations from your Cloud Database here
    # user_annotations = db.get_user_annotations(email)
    
    # --- Dummy Logic to prevent crashing while you set up a DB ---
    user_annotations = [] 
    if len(user_annotations) >= MAX_QUOTA:
        return {"status": "complete", "message": "Quota reached. Thank you!"}

    # Find the next scenario this user hasn't annotated yet
    annotated_ids = [] # Replace with actual DB IDs
    available_scenarios = scenarios_df[~scenarios_df['delivery_id'].isin(annotated_ids)]

    if available_scenarios.empty:
        return {"status": "complete", "message": "No more scenarios available!"}

    next_task = available_scenarios.iloc[0].fillna("none").to_dict()
    return {"status": "active", "task": next_task, "progress": len(user_annotations)}

@app.post("/submit")
def submit_annotation(req: SubmitRequest):
    # ❌ THIS WILL NOT WORK ON VERCEL:
    # with open("annotations.csv", "a") as f:
    #     f.write(...)
    
    # ✅ TODO: Insert into Cloud Database
    # db.execute("INSERT INTO annotations (email, delivery_id, policy) VALUES (?, ?, ?)", ...)
    
    return {"message": "Saved successfully"}

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()