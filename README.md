# ResumeAiGenModel
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/vaibhavjain2005/ResumeAiGenModel)

An intelligent resume generator that tailors your resume to a specific job description using a dual AI model approach. This project leverages a fine-tuned T5 model for creative text generation and the Gemini API for keyword extraction and relevance ranking, all served via a FastAPI backend with a React frontend.

## Features

- **AI-Powered Tailoring**: Dynamically adapts your resume content to match the requirements of a target job description.
- **Dual-AI Architecture**:
    - **Google Gemini**: Extracts keywords, reorders skills, and filters projects based on job relevance.
    - **Fine-tuned Flan-T5**: Rewrites experience bullets, enhances project descriptions, and generates impactful professional summaries.
- **Job Match Score**: Calculates a percentage score indicating how well your resume aligns with the job description's keywords.
- **Interactive UI**: A modern React and Vite frontend with HeroUI components for a smooth user experience.
- **PDF Export**: Download the AI-generated resume as a clean, professionally formatted PDF.

## How It Works

The application operates through a seamless flow between the frontend and a powerful AI backend.

1.  **Data Input**: The user enters their resume details (personal info, education, experience, projects, skills) and the target job description into the React frontend.
2.  **API Request**: The frontend bundles the data into a JSON object and sends a `POST` request to the FastAPI backend.
3.  **Gemini-Powered Analysis**:
    - The backend first calls the Gemini API to extract key skills and technologies from the job description.
    - It then uses Gemini to reorder the user's skills and filter their projects, prioritizing those most relevant to the job.
4.  **T5-Powered Content Generation**:
    - A fine-tuned T5 model rewrites and enhances the descriptions for the user's professional experience and selected projects.
    - It also generates a concise, tailored professional summary based on the job role and top skills.
5.  **Response and Rendering**: The backend calculates a match score and returns a final JSON object containing the fully tailored resume. The React frontend receives this data and renders it in a clean, readable format.
6.  **PDF Generation**: The user can then download the generated resume as a PDF, created on the client-side using `jsPDF` and `html2canvas`.

## Tech Stack

| Component      | Technology                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| **Frontend**   | React, Vite, Tailwind CSS, HeroUI, Framer Motion                                                             |
| **Backend**    | Python, FastAPI, Uvicorn                                                                                     |
| **AI Models**  | [jain05vaibhav/t5-further-finer](https://huggingface.co/jain05vaibhav/t5-further-finer), Google Gemini          |
| **AI Toolkit** | Hugging Face Transformers, Google Generative AI SDK                                                          |
| **PDF Export** | jsPDF, html2canvas                                                                                             |

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js and npm

### Backend Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/vaibhavjain2005/ResumeAiGenModel.git
    cd ResumeAiGenModel
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure API Key:**
    Open `final_json_output.py` and replace the placeholder with your actual Google Gemini API key:
    ```python
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
    ```

5'  **Run the backend server:**
    The server will run on `http://localhost:8000`.
    ```sh
    uvicorn api:app --reload
    ```

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```sh
    npm install
    ```

3.  **Run the frontend development server:**
    The application will be accessible at `http://localhost:5173`.
    ```sh
    npm run dev
    ```

## API Endpoint

The primary endpoint for generating a resume.

- **URL**: `/generate-resume`
- **Method**: `POST`
- **Request Body**: A JSON object containing the user's resume data and the job description.

**Example Request:**
```json
{
  "job_description": "We are looking for a Python Developer with experience in Machine Learning...",
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
      "description": "Developed web applications using Python and Flask."
    }
  ],
  "projects": [
    {
      "name": "NLP Chatbot",
      "technologies": "Python, TensorFlow, NLP",
      "description": "Built an intelligent chatbot using NLP techniques."
    }
  ],
  "skills": ["JavaScript", "Python", "React", "TensorFlow", "PyTorch"]
}
```

**Example Success Response:**
```json
{
    "success": true,
    "keywords_extracted": ["Python", "Machine Learning", "NLP", "TensorFlow", "PyTorch"],
    "professional_summary": "Results-driven Python Developer with expertise in Machine Learning and NLP...",
    "personal_info": { ... },
    "education": [ ... ],
    "experience": [ ... ], // With enhanced descriptions
    "projects": [ ... ], // With filtered projects and enhanced descriptions
    "skills": ["Python", "TensorFlow", "PyTorch", "NLP", "React", "JavaScript"], // Reordered
    "match_score": 85.5,
    "ai_enhancements": { ... }
}
```

## Model Training

The `google/flan-t5-base` model was fine-tuned for text enhancement tasks (e.g., rewriting experience bullets, generating summaries).

-   **Training Script**: `flan-t5-resume-model-training-stable.py`
-   **Training Data**: Located in the `fine_tuning_data/` directory. The data consists of `input`/`output` pairs designed to teach the model how to professionally rewrite resume content.
-   **Fine-tuned Model**: The trained model is available on Hugging Face at [jain05vaibhav/t5-further-finer](https://huggingface.co/jain05vaibhav/t5-further-finer).