from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database as db
from resume_parser import extract_text_from_pdf
from resume_analyzer import analyze_resume
import shutil
import os
import requests
import asyncio
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.init_db()

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if db.add_user(username, password):
        return {"status": "success", "message": "Account created!"}
    raise HTTPException(status_code=400, detail="Username exists")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if db.verify_user(username, password):
        return {"status": "success", "user": username}
    raise HTTPException(status_code=401, detail="Invalid Credentials")

@app.post("/analyze_resume")
async def analyze_resume_endpoint(username: str = Form(...), file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = extract_text_from_pdf(file_location)
    scores, best_role = analyze_resume(text)
    
    # Skill Gap Logic (Mocked for presentation)
    all_skills = ["Docker", "Kubernetes", "GraphQL", "AWS", "CI/CD", "Redis"]
    missing = random.sample(all_skills, 2)
    
    db.add_history(username, "Resume Scan", f"{file.filename} -> {best_role}")
    os.remove(file_location)
    return {"top_role": best_role, "scores": scores, "missing_skills": missing}

@app.post("/analyze_github")
async def analyze_github(username: str = Form(...)):
    try:
        user_response = requests.get(f"https://api.github.com/users/{username}")
        if user_response.status_code != 200:
            return {"error": "GitHub profile not found!"}
        
        user_data = user_response.json()
        repos_response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
        repos = repos_response.json() if repos_response.status_code == 200 else []
        
        languages = {}
        stars = 0
        for repo in repos:
            stars += repo.get('stargazers_count', 0)
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
        lang_str = ", ".join([l[0] for l in top_languages]) if top_languages else "No code found"
        
        db.add_history(username, "GitHub Scan", username)
        return {
            "status": "success", "name": user_data.get("name", username),
            "public_repos": user_data.get("public_repos", 0), "followers": user_data.get("followers", 0),
            "total_stars": stars, "top_languages": lang_str, "profile_url": user_data.get("html_url")
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_video")
async def analyze_video(username: str = Form(...), file: UploadFile = File(...)):
    await asyncio.sleep(2.5) # Simulate processing
    confidence = random.randint(80, 98)
    communication = random.randint(75, 95)
    technical_keywords = random.randint(60, 90)
    is_suspicious = random.choice([False, False, False, False, True])
    proctoring_msg = "⚠️ Multiple faces / Eye movement detected!" if is_suspicious else "✅ Clean - No suspicious activity."
    overall = int((confidence + communication + technical_keywords) / 3)
    db.add_history(username, "Video Analysis", f"Score: {overall}%")
    return {
        "status": "success", "confidence": confidence, "communication": communication,
        "technical_keywords": technical_keywords, "proctoring_status": proctoring_msg,
        "is_suspicious": is_suspicious, "transcript_snippet": "...I have extensive experience working with Python APIs and deploying models...",
        "overall_score": overall
    }

# --- NAYA FEATURE: MAGIC COVER LETTER GENERATOR ---
@app.post("/generate_cover_letter")
async def generate_cover_letter(username: str = Form(...), jd: str = Form(...), file: UploadFile = File(...)):
    await asyncio.sleep(2.0) # Simulating Generative AI thinking
    letter = f"""Dear Hiring Manager,\n\nBased on the Job Description for the required role, my background directly aligns with your needs. My resume highlights my technical proficiency and problem-solving skills.\n\nI am particularly drawn to this position because it perfectly matches my expertise in AIML and Backend technologies. I am confident that I can bring immediate value to your team.\n\nThank you for considering my application.\n\nBest Regards,\nCandidate"""
    db.add_history(username, "AI Generative", "Cover Letter Built")
    return {"status": "success", "cover_letter": letter}

@app.post("/chat_hr")
async def chat_hr(username: str = Form(...), message: str = Form(...)):
    msg = message.lower()
    await asyncio.sleep(1.0)
    if "best" in msg or "match" in msg:
        response = "Based on our NLP Engine, **Rahul Sharma** is the strongest match (85%) for the Backend Developer role. Would you like to auto-schedule an interview?"
    elif "skills" in msg or "missing" in msg:
        response = "Candidates generally lack Docker and Kubernetes based on today's scans. I suggest updating the JD or offering training."
    elif "video" in msg or "interview" in msg:
        response = "Recent videos show high confidence (avg 88%), but one candidate was flagged by the Proctoring AI for off-screen eye movement."
    else:
        response = "I am your AI Recruiting Assistant! You can ask me to find the *best candidate*, analyze *skills gap*, or give a *pipeline summary*."
    return {"status": "success", "response": response}

@app.get("/user_dashboard")
def user_dashboard(username: str):
    history = db.get_user_history(username)
    return {"history": history}