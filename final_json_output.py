from transformers import T5Tokenizer, T5ForConditionalGeneration
import google.generativeai as genai
import json

model_path = "jain05vaibhav/flan-t5-resume-further-trained"
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained(model_path)
print("Model loaded successfully")

GEMINI_API_KEY = "GEMINI API KEY "  
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')  


def extract_keywords_from_job(job_description):
    """Extract important keywords from job description"""
    prompt = f"""Extract key skills and technologies from this job posting. List only the most important ones as comma-separated keywords.

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


def reorder_skills_by_relevance(skills, job_description):
    """Use Gemini API to reorder skills based on job description relevance"""
    if not skills:
        return []

    try:
        skills_text = "\n".join([f"{idx + 1}. {skill}" for idx, skill in enumerate(skills)])

        prompt = f"""Given this job description:
{job_description}

And these skills:
{skills_text}

Reorder ALL skills by relevance to the job description. Return ONLY a JSON array with the indices (1-based) of skills in order of relevance (most relevant first).

For example, if skill 3 is most relevant, then skill 1, then skill 5, return: [3, 1, 5, ...]

Include ALL skills in the output, just reordered by relevance.
Return ONLY the JSON array, no explanation."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        ranking_indices = extract_and_validate_json(response_text, expected_length=len(skills))

        if ranking_indices:
            reordered_skills = []
            for idx in ranking_indices:
                if 1 <= idx <= len(skills):
                    reordered_skills.append(skills[idx - 1])
            for skill in skills:
                if skill not in reordered_skills:
                    reordered_skills.append(skill)
            return reordered_skills
        else:
            return skills

    except Exception as e:
        print(f"Error in Gemini skill reordering: {e}")
        return skills


def sort_projects_by_relevance(projects, job_description):
    """Use Gemini API to filter and return ALL relevant projects ranked by relevance"""
    if not projects:
        return []

    try:
        projects_text = ""
        for idx, project in enumerate(projects):
            projects_text += f"\n{idx + 1}. {project.get('name', 'Unnamed Project')}\n"
            projects_text += f"   Technologies: {project.get('technologies', 'N/A')}\n"
            projects_text += f"   Description: {project.get('description', 'N/A')}\n"

        prompt = f"""Given this job description:
{job_description}

And these projects:
{projects_text}

Analyze each project and return ONLY the indices (1-based) of projects that are RELEVANT and match the job description, ordered by relevance (most relevant first).

Consider:
- Does the technology stack align with job requirements?
- Do the skills demonstrated match what's needed?
- Is the domain/industry relevant?
- Would this project showcase relevant experience?

REJECT projects that don't match the job requirements.
INCLUDE ONLY projects that are relevant.
ORDER them from most to least relevant.

Return ONLY a JSON array with the indices of relevant projects in order of relevance.
For example: [3, 1, 7] (if only projects 3, 1, and 7 are relevant, in that order)

If no projects are relevant, return an empty array: []
Return ONLY the JSON array, no explanation."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        ranking_indices = extract_and_validate_json(response_text, expected_length=None)

        if ranking_indices is not None:
            relevant_projects = []
            for idx in ranking_indices:
                if 1 <= idx <= len(projects):
                    relevant_projects.append(projects[idx - 1])
            return relevant_projects
        else:
            print("JSON validation failed, returning all projects as fallback")
            return projects

    except Exception as e:
        print(f"Error in Gemini project filtering: {e}")
        return projects


def extract_and_validate_json(response_text, expected_length=None):
    """Extract and validate JSON array from Gemini response"""
    try:
        if '[' in response_text and ']' in response_text:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            json_str = response_text[start:end]

            parsed_json = json.loads(json_str)

            if not isinstance(parsed_json, list):
                print("JSON validation failed: Not a list")
                return None

            if not all(isinstance(x, int) for x in parsed_json):
                print("JSON validation failed: Not all elements are integers")
                return None

            if expected_length and len(parsed_json) != expected_length:
                print(f"JSON validation warning: Expected {expected_length} items, got {len(parsed_json)}")

            if not all(x > 0 for x in parsed_json):
                print("JSON validation failed: Contains non-positive indices")
                return None

            print(f"✅ JSON validated successfully: {parsed_json}")
            return parsed_json
        else:
            print("JSON validation failed: No array found in response")
            return None

    except json.JSONDecodeError as e:
        print(f"JSON validation failed: Invalid JSON - {e}")
        return None
    except Exception as e:
        print(f"JSON validation failed: {e}")
        return None


def tailor_resume_experience(experience_text):
    """Rewrite experience bullet - OPTIMIZED for your training dataset format"""
    prompt = f"""Rewrite professionally: {experience_text}

"""

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=150,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    improved = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(improved) < 10:
        return experience_text
    return improved.strip()


def tailor_project_description(project_name, project_tech):
    """Enhance project description - OPTIMIZED for your training dataset format"""
    prompt = f"""Enhance project: {project_name} using {project_tech}

Enhanced description:"""

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=200,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    improved = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(improved) < 15:
        return f"Project using {project_tech}"
    return improved.strip()


def generate_professional_summary(role, experience_count, top_skills):
    """Generate professional summary - OPTIMIZED for your training dataset format"""
    skills_str = ", ".join(top_skills[:5])

    prompt = f"""Create professional summary: {role}, {experience_count} years, {skills_str}

Professional summary:"""

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=120,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True,
        length_penalty=1.0
    )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(summary) < 30:
        summary = f"Results-driven {role} with {experience_count} years of experience in {', '.join(top_skills[:3])}. Proven track record of delivering high-quality solutions."

    return summary.strip()


def generate_tailored_resume(job_description, personal_info, education, experience, projects, skills):
    """
    Main function to generate a complete tailored resume
    
    Args:
        job_description (str): The target job description
        personal_info (dict): Personal information (name, email, phone, etc.)
        education (list): List of education entries
        experience (list): List of work experience entries with bullets
        projects (list): List of project entries
        skills (list): List of skills
    
    Returns:
        dict: Complete resume data with AI enhancements
    """

    print("🚀 Starting resume generation...")

    print("\n1. Extracting keywords from job description...")
    keywords = extract_keywords_from_job(job_description)
    keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]
    print(f"   Found {len(keywords_list)} keywords: {keywords_list}")

    print(f"\n2. Reordering {len(skills)} skills with Gemini...")
    reordered_skills = reorder_skills_by_relevance(skills, job_description)
    print(f"   ✅ Skills reordered")

    print(f"\n3. Filtering and ranking {len(projects)} projects with Gemini...")
    relevant_projects = sort_projects_by_relevance(projects, job_description)
    print(f"   ✅ Selected {len(relevant_projects)} relevant projects from {len(projects)} total")

    print("\n4. Generating professional summary...")
    first_role = "Professional"
    if experience and len(experience) > 0:
        first_role = experience[0].get('title', 'Professional')

    professional_summary = generate_professional_summary(first_role, len(experience), reordered_skills)
    print(f"   ✅ Summary generated")

    print("\n5. Tailoring experience bullets...")
    tailored_experience = []
    for exp in experience:
        tailored_bullets = []
        for bullet in exp.get("bullets", []):
            if len(bullet) > 10:
                improved = tailor_resume_experience(bullet)
                tailored_bullets.append(improved)
            else:
                tailored_bullets.append(bullet)

        tailored_experience.append({
            **exp,
            "bullets": tailored_bullets
        })
    print(f"   ✅ Experience tailored")

    print("\n6. Tailoring project descriptions...")
    tailored_projects = []
    for project in relevant_projects:
        project_name = project.get("name", "Unnamed Project")
        project_tech = project.get("technologies", "")

        if len(project_tech) > 5:
            tailored_desc = tailor_project_description(project_name, project_tech)
        else:
            tailored_desc = project.get("description", "")

        tailored_projects.append({
            **project,
            "description": tailored_desc
        })
    print(f"   ✅ Projects tailored")

    match_score = 0
    if keywords_list and reordered_skills:
        matched = sum(1 for k in keywords_list if any(k.lower() in s.lower() for s in reordered_skills))
        match_score = (matched / len(keywords_list)) * 100

    resume_data = {
        "success": True,
        "keywords_extracted": keywords_list,
        "professional_summary": professional_summary,
        "personal_info": personal_info,
        "education": education,
        "experience": tailored_experience,
        "projects": tailored_projects,
        "skills": reordered_skills,
        "match_score": round(match_score, 1),
        "ai_enhancements": {
            "skills_reordered": True,
            "skills_count": len(reordered_skills),
            "total_projects_submitted": len(projects),
            "projects_selected": len(tailored_projects),
            "projects_rejected": len(projects) - len(tailored_projects),
            "note": "ALL relevant projects are included, ranked by relevance"
        }
    }

    print("\n✅ Resume generation complete!")
    return resume_data


# Example usage
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
        {
            "degree": "Bachelor of Computer Science",
            "university": "Example University",
            "year": "2020"
        }
    ]

    exp = [
        {
            "title": "Software Developer",
            "company": "Tech Corp",
            "duration": "2020-2023",
            "bullets": [
                "Developed web applications using Python and Flask",
                "Implemented machine learning models for data analysis",
                "Collaborated with team of 5 developers"
            ]
        }
    ]

    proj = [
        {
            "name": "NLP Chatbot",
            "technologies": "Python, TensorFlow, NLP",
            "description": "Built an intelligent chatbot using NLP techniques"
        },
        {
            "name": "E-commerce Website",
            "technologies": "JavaScript, React, Node.js",
            "description": "Created a full-stack e-commerce platform"
        },
        {
            "name": "ML Image Classifier",
            "technologies": "Python, PyTorch, CNN",
            "description": "Developed image classification system using deep learning"
        }
    ]

    skill_list = [
        "JavaScript", "Python", "React", "TensorFlow", "PyTorch",
        "NLP", "Flask", "Docker", "AWS", "SQL"
    ]

    result = generate_tailored_resume(
        job_description=job_desc,
        personal_info=personal,
        education=edu,
        experience=exp,
        projects=proj,
        skills=skill_list
    )

    print("\n" + "="*70)
    print("GENERATED RESUME DATA:")
    print("="*70)
    print(json.dumps(result, indent=2))
