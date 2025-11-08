import json
import requests

def test_resume_generation():
    # Test data
    test_data = {
        "job_description": """
        We are looking for a Python Developer with experience in Machine Learning and NLP.
        Required skills: Python, TensorFlow, PyTorch, NLP, API development, Flask.
        """,
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        },
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "university": "Example University",
                "year": "2020"
            }
        ],
        "experience": [
            {
                "title": "Software Developer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": "Developed and deployed web applications using Python and Flask. Implemented machine learning models for data analysis and optimized NLP pipelines."
            }
        ],
        "projects": [
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
        ],
        "skills": [
            "JavaScript", "Python", "React", "TensorFlow", 
            "PyTorch", "NLP", "Flask", "Docker", "AWS", "SQL"
        ]
    }

    try:
        # Make POST request to the API
        response = requests.post(
            "http://localhost:8000/generate-resume",
            json=test_data
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Print the response
        print("\n" + "="*70)
        print("API RESPONSE:")
        print("="*70)
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")

if __name__ == "__main__":
    test_resume_generation()