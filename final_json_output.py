from transformers import T5Tokenizer, T5ForConditionalGeneration
import google.generativeai as genai
import json
from typing import Dict, List, Union, Any


# ==============================
# 🔧 Model Initialization
# ==============================
model_path = "jain05vaibhav/t5-further-finer"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)
print("✅ T5 model loaded successfully")

# Gemini configuration
GEMINI_API_KEY = "AIzaSyCvabMU_CgDDHuJCSCE1pC65Sw4aNouBSY"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


# ==============================
# 🧠 Utility Functions
# ==============================
def extract_and_validate_json(response_text, expected_length=None):
    """Extract and validate JSON array from Gemini response"""
    try:
        if "[" in response_text and "]" in response_text:
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            json_str = response_text[start:end]
            parsed_json = json.loads(json_str)

            if not isinstance(parsed_json, list):
                print("⚠️ JSON validation failed: Not a list")
                return None

            if expected_length and len(parsed_json) != expected_length:
                print(f"⚠️ JSON validation warning: Expected {expected_length} items, got {len(parsed_json)}")

            print(f"✅ JSON validated successfully: {parsed_json}")
            return parsed_json
        else:
            print("⚠️ JSON validation failed: No array found in response")
            return None
    except Exception as e:
        print(f"⚠️ JSON validation failed: {e}")
        return None


# ==============================
# 🌟 Gemini Keyword Extraction
# ==============================
def extract_keywords_from_job(job_description):
    """
    Extract important keywords (skills, tools, technologies) from job description using Gemini.
    Returns a list of keywords.
    """
    try:
        prompt = f"""
You are an expert technical recruiter.
Extract the most important skills, tools, and technologies from the following job description.
Return ONLY a comma-separated list of keywords (no explanation, no JSON).

Job Description:
{job_description}

Important keywords:
"""
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()

        # Split by comma or newline
        keywords = [k.strip() for k in text.replace("\n", ",").split(",") if k.strip()]
        print(f"✅ Extracted {len(keywords)} keywords from Gemini: {keywords}")
        return keywords
    except Exception as e:
        print(f"⚠️ Error extracting keywords via Gemini: {e}")
        return []


# ==============================
# 🔮 Gemini Skill & Project Ranking
# ==============================
def reorder_skills_by_relevance(skills, job_description):
    """Use Gemini API to reorder skills based on job description relevance"""
    if not skills:
        return []

    try:
        skills_text = "\n".join([f"{i + 1}. {s}" for i, s in enumerate(skills)])
        prompt = f"""Given this job description:
{job_description}

And these skills:
{skills_text}

Reorder ALL skills by relevance to the job description.
Return ONLY a JSON array with the indices (1-based) of skills in order of relevance.
Example: [3, 1, 5, 2, 4]
Return ONLY the JSON array, no explanation.
"""

        response = gemini_model.generate_content(prompt)
        ranking_indices = extract_and_validate_json(response.text.strip(), expected_length=len(skills))

        if ranking_indices:
            reordered = [skills[i - 1] for i in ranking_indices if 1 <= i <= len(skills)]
            for s in skills:
                if s not in reordered:
                    reordered.append(s)
            return reordered
        return skills
    except Exception as e:
        print(f"⚠️ Error in Gemini skill reordering: {e}")
        return skills


def sort_projects_by_relevance(projects, job_description):
    """Use Gemini API to return relevant projects by job match; fallback to all if none"""
    if not projects:
        return []

    try:
        projects_text = ""
        for i, p in enumerate(projects):
            projects_text += f"\n{i + 1}. {p.get('name', 'Unnamed Project')}\n"
            projects_text += f"   Technologies: {p.get('technologies', 'N/A')}\n"
            projects_text += f"   Description: {p.get('description', 'N/A')}\n"

        prompt = f"""Given this job description:
{job_description}

And these projects:
{projects_text}

Return ONLY a JSON array with the indices (1-based) of projects that are RELEVANT and match the job description,
ordered by relevance (most relevant first).
If no projects are relevant, return [].
Return ONLY the JSON array, no explanation.
"""

        response = gemini_model.generate_content(prompt)
        ranking_indices = extract_and_validate_json(response.text.strip())

        if ranking_indices is not None:
            relevant_projects = [projects[i - 1] for i in ranking_indices if 1 <= i <= len(projects)]
            if len(relevant_projects) == 0:
                print("⚠️ No relevant projects found — using all projects as fallback")
                return projects

            print(f"✅ Found {len(relevant_projects)} relevant projects")
            return relevant_projects

        print("⚠️ JSON validation failed — returning all projects as fallback")
        return projects

    except Exception as e:
        print(f"⚠️ Error in Gemini project filtering: {e}")
        return projects


# ==============================
# ✨ T5 Text Enhancement
# ==============================
def tailor_resume_experience(experience_text):
    """Rewrite experience professionally using T5"""
    prompt = f"Rewrite professionally: {experience_text}"
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs, max_length=150, num_beams=4,
        no_repeat_ngram_size=2, early_stopping=True
    )
    improved = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return improved.strip() if len(improved) > 10 else experience_text


def tailor_project_description(project_name, project_tech):
    """Enhance project description"""
    prompt = f"Enhance project: {project_name} using {project_tech}\nEnhanced description:"
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=200, num_beams=4, no_repeat_ngram_size=2, early_stopping=True)
    improved = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return improved.strip() if len(improved) > 15 else f"Project using {project_tech}"


def generate_professional_summary(role, experience_count, top_skills):
    """Generate short professional summary"""
    skills_str = ", ".join(top_skills[:5])
    prompt = f"Create professional summary: {role}, {experience_count} years, {skills_str}\nProfessional summary:"

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs, max_length=120, num_beams=4,
        no_repeat_ngram_size=2, early_stopping=True
    )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(summary) < 30:
        summary = f"Results-driven {role} with {experience_count} years of experience in {', '.join(top_skills[:3])}. Proven track record of delivering high-quality solutions."
    return summary.strip()


# ==============================
# 🧾 Resume Generation Pipeline
# ==============================
def generate_tailored_resume(
    job_description: str,
    personal_info: Dict[str, str],
    education: List[Dict[str, str]],
    experience: List[Dict[str, Union[str, List[str]]]],
    projects: List[Dict[str, str]],
    skills: List[str]
) -> Dict[str, Any]:

    print("🚀 Starting resume generation...")

    # ✅ Step 1: Extract keywords using Gemini
    keywords_list = extract_keywords_from_job(job_description)

    # ✅ Step 2: Reorder skills using Gemini
    reordered_skills = reorder_skills_by_relevance(skills, job_description)

    # ✅ Step 3: Sort projects by relevance using Gemini
    relevant_projects = sort_projects_by_relevance(projects, job_description)

    # ✅ Step 4: Generate professional summary using T5
    first_role = experience[0].get("title", "Professional") if experience else "Professional"
    professional_summary = generate_professional_summary(first_role, len(experience), reordered_skills)

    # ✅ Step 5: Tailor experiences
    tailored_experience = []
    for exp in experience:
        if "description" in exp and isinstance(exp["description"], str):
            desc = exp["description"]
            if len(desc.strip()) > 10:
                exp["description"] = tailor_resume_experience(desc)
            tailored_experience.append(exp)
        elif "bullets" in exp and isinstance(exp["bullets"], list):
            improved_bullets = [tailor_resume_experience(b) if len(b) > 10 else b for b in exp["bullets"]]
            exp["bullets"] = improved_bullets
            tailored_experience.append(exp)
        else:
            tailored_experience.append(exp)
    print("✅ Experience tailored")

    # ✅ Step 6: Enhance project descriptions
    tailored_projects = []
    for p in relevant_projects:
        tech = p.get("technologies", "")
        desc = p.get("description", "")
        improved = tailor_project_description(p.get("name", "Unnamed Project"), tech) if len(tech) > 5 else desc
        tailored_projects.append({**p, "description": improved})
    print("✅ Projects tailored")

    # ✅ Step 7: Compute match score
    matched = sum(1 for k in keywords_list if any(k.lower() in s.lower() for s in reordered_skills))
    match_score = round((matched / len(keywords_list)) * 100, 1) if keywords_list else 0

    # ✅ Step 8: Final resume structure
    resume_data = {
        "success": True,
        "keywords_extracted": keywords_list,
        "professional_summary": professional_summary,
        "personal_info": personal_info,
        "education": education,
        "experience": tailored_experience,
        "projects": tailored_projects,
        "skills": reordered_skills,
        "match_score": match_score,
        "ai_enhancements": {
            "skills_reordered": True,
            "skills_count": len(reordered_skills),
            "total_projects_submitted": len(projects),
            "projects_selected": len(tailored_projects),
            "projects_rejected": len(projects) - len(tailored_projects),
            "note": "Keywords extracted using Gemini; relevant projects selected by Gemini."
        }
    }

    print("🎯 Resume generation complete!")
    return resume_data


# ==============================
# 🧩 Entry Point
# ==============================
if __name__ == "__main__":
    print("This module is intended to be imported. Run API server or tests instead.")
