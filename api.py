from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS middleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
from final_json_output import generate_tailored_resume

app = FastAPI(
    title="Resume Generator API",
    description="API for generating AI-tailored resumes based on job descriptions",
    version="1.0.0"
)

# ✅ Allow CORS for frontend (React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend like ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Request Models
# =========================
class Education(BaseModel):
    degree: str
    university: str
    year: str

class Experience(BaseModel):
    title: str
    company: str
    duration: str
    description: Optional[str] = None
    bullets: Optional[List[str]] = None

class Project(BaseModel):
    name: str
    technologies: str
    description: str

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str

class ResumeRequest(BaseModel):
    job_description: str = Field(..., description="The job description to tailor the resume for")
    personal_info: PersonalInfo
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]
    skills: List[str] = Field(..., description="List of skills")

# =========================
# Endpoint
# =========================
@app.post("/generate-resume")
async def generate_resume(request: ResumeRequest):
    try:
        result = generate_tailored_resume(
            request.job_description,
            request.personal_info.dict(),
            [edu.dict() for edu in request.education],
            [exp.dict() for exp in request.experience],
            [proj.dict() for proj in request.projects],
            request.skills
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Run Server
# =========================
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
