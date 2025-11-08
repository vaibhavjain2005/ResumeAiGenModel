from transformers import T5Tokenizer, T5ForConditionalGeneration
import google.generativeai as genai
import json


model_path = "jain05vaibhav/flan-t5-resume-further-trained"
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained(model_path)
print("✅ Model loaded successfully")

GEMINI_API_KEY = "AIzaSyCvabMU_CgDDHuJCSCE1pC65Sw4aNouBSY"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')



def extract_keywords_from_job(job_description):
    """Extract important keywords from job description using T5"""
    prompt = f"""Extract key skills and technologies from this job posting. 
List only the most important ones as comma-separated keywords.

Job Description: {job_description}

Important keywords:"""

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=100,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    keywords = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return keywords.strip()


def extract_and_validate_json(response_text, expected_length=None):
    """Extract and validate JSON array from Gemini response"""
    try:
        if '[' in response_text and ']' in response_text:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            json_str = response_text[start:end]
            parsed_json = json.loads(json_str)

            if not isinstance(parsed_json, list):
                print("⚠️ JSON validation failed: Not a list")
                return None

            if not all(isinstance(x, int) for x in parsed_json):
                print("⚠️ JSON validation failed: Not all elements are integers")
                return None

            if expected_length and len(parsed_json) != expected_length:
                print(f"⚠️ JSON validation warning: Expected {expected_length} items, got {len(parsed_json)}")

            if not all(x > 0 for x in parsed_json):
                print("⚠️ JSON validation failed: Contains non-positive indices")
                return None

            print(f"✅ JSON validated successfully: {parsed_json}")
            return parsed_json
        else:
            print("⚠️ JSON validation failed: No array found in response")
            return None
    except Exception as e:
        print(f"⚠️ JSON validation failed: {e}")
        return None



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
For example: [3, 1, 5, ...]
Include ALL skills in the output, just reordered by relevance.
Return ONLY the JSON array, no explanation."""

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
Return ONLY the JSON array, no explanation."""

        response = gemini_model.generate_content(prompt)
        ranking_indices = extract_and_validate_json(response.text.strip(), expected_length=None)

        if ranking_indices is not None:
            relevant_projects = [projects[i - 1] for i in ranking_indices if 1 <= i <= len(projects)]

            # 🧠 Fallback: If Gemini found no relevant projects, use all
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



def generate_tailored_resume(job_description, personal_info, education, experience, projects, skills):
    """Generates full AI-tailored resume"""
    print("🚀 Starting resume generation...")

   
    keywords = extract_keywords_from_job(job_description)
    keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]
    print(f"✅ Extracted {len(keywords_list)} keywords: {keywords_list}")

    reordered_skills = reorder_skills_by_relevance(skills, job_description)

   
    relevant_projects = sort_projects_by_relevance(projects, job_description)

  
    first_role = experience[0].get("title", "Professional") if experience else "Professional"
    professional_summary = generate_professional_summary(first_role, len(experience), reordered_skills)

  
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

    
    tailored_projects = []
    for p in relevant_projects:
        tech = p.get("technologies", "")
        desc = p.get("description", "")
        improved = tailor_project_description(p.get("name", "Unnamed Project"), tech) if len(tech) > 5 else desc
        tailored_projects.append({**p, "description": improved})
    print("✅ Projects tailored")

  
    matched = sum(1 for k in keywords_list if any(k.lower() in s.lower() for s in reordered_skills))
    match_score = round((matched / len(keywords_list)) * 100, 1) if keywords_list else 0

   
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
            "note": "Relevant projects selected by Gemini; fallback used if none found."
        }
    }

    print("🎯 Resume generation complete!")
    return resume_data


# ==============================
# Example usage
# ==============================

if __name__ == "__main__":
    job_desc = """
    We are looking for a Python Developer with experience in Machine Learning and NLP.
    Required skills: Python, TensorFlow, PyTorch, NLP, API development, Flask.
    """

    personal = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    }

    edu = [
        {"degree": "Bachelor of Computer Science", "university": "Example University", "year": "2020"}
    ]

    # Paragraph-style experience (text box input)
    exp = [
        {
            "title": "Software Developer",
            "company": "Tech Corp",
            "duration": "2020-2023",
            "description": "Developed and deployed web applications using Python and Flask. Implemented machine learning models for data analysis and optimized NLP pipelines."
        }
    ]

    proj = [
        {"name": "NLP Chatbot", "technologies": "Python, TensorFlow, NLP", "description": "Built an intelligent chatbot using NLP techniques"},
        {"name": "E-commerce Website", "technologies": "JavaScript, React, Node.js", "description": "Created a full-stack e-commerce platform"},
        {"name": "ML Image Classifier", "technologies": "Python, PyTorch, CNN", "description": "Developed image classification system using deep learning"}
    ]

    skills = ["JavaScript", "Python", "React", "TensorFlow", "PyTorch", "NLP", "Flask", "Docker", "AWS", "SQL"]

    result = generate_tailored_resume(job_desc, personal, edu, exp, proj, skills)

    print("\n" + "="*70)
    print("GENERATED RESUME DATA:")
    print("="*70)
    print(json.dumps(result, indent=2))
