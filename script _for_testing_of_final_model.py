"""
Test Script for Fine-Tuned T5 Resume Model

Tests the model on various resume generation tasks.
This script is specifically designed to load a model fine-tuned from
Hugging Face's T5/FLAN-T5 architecture.
"""

import os
# Suppress TensorFlow logging if used, though this script uses PyTorch
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import torch

try:
    # We use T5 classes as Flan-T5 uses the same architecture and tokenization
    from transformers import T5Tokenizer, T5ForConditionalGeneration
except Exception as e:
    print("\n" + "="*70)
    print("ERROR: Failed to import transformers")
    print("="*70)
    print(f"\nError: {e}\n")
    print("Please ensure the 'transformers' and 'torch' libraries are installed.")
    print("="*70)
    raise

print("="*70)
print("T5/Flan-T5 Resume Model Testing")
print("="*70)

# Configuration
# IMPORTANT: This path MUST point to the directory where your fine-tuned model
# (including pytorch_model.bin and tokenizer_config.json) is saved.
MODEL_PATH = "./flan-t5-base-resume-finetuned-stable/final_model"
MAX_INPUT_LENGTH = 128
MAX_OUTPUT_LENGTH = 256

# Check if model exists
if not os.path.exists(MODEL_PATH) or not os.path.exists(os.path.join(MODEL_PATH, "pytorch_model.bin")):
    print(f"\n❌ Error: Model files not found in the expected directory: {MODEL_PATH}")
    print("\nPlease verify the path or run the training script first.")
    exit(1)

# Load model
print(f"\nLoading model from: {MODEL_PATH}")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}\n")

# Use T5Tokenizer for loading Flan-T5 models
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

print("✓ Model loaded successfully\n")

# Test examples
test_cases = [
    {
        "category": "Professional Summary (Software)",
        "input": "Create professional summary: Software Engineering, 5 years, Python, AWS, Docker"
    },
    {
        "category": "Professional Summary (Data Science)",
        "input": "Create professional summary: Data Science, 7 years, Machine Learning, Python, TensorFlow"
    },
    {
        "category": "Experience Bullet (Development)",
        "input": "Rewrite professionally: Built web applications using Python, Django, PostgreSQL"
    },
    {
        "category": "Experience Bullet (Analysis)",
        "input": "Rewrite professionally: Analyzed data using Python, SQL, Tableau"
    },
    {
        "category": "Experience Bullet (Management)",
        "input": "Rewrite professionally: Managed team using Agile, Scrum"
    },
    {
        "category": "Project Description (Web)",
        "input": "Enhance project: E-commerce Platform using React, Node.js, MongoDB"
    },
    {
        "category": "Project Description (ML)",
        "input": "Enhance project: Machine Learning Model using Python, TensorFlow"
    },
]

print("="*70)
print("Running Test Cases")
print("="*70)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'─'*70}")
    print(f"Test {i}/{len(test_cases)}: {test['category']}")
    print(f"{'─'*70}")
    print(f"Input:\n  {test['input']}")

    # Tokenize input
    inputs = tokenizer(
        test['input'],
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Generate output
    # Recommended generation parameters for T5-based models:
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=MAX_OUTPUT_LENGTH,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
            length_penalty=1.2
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\nOutput:\n  {result}")

print("\n" + "="*70)
print("Testing Complete!")
print("="*70)

# Interactive mode
print("\n" + "─"*70)
print("Interactive Mode")
print("─"*70)
print("\nYou can now test your own prompts.")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Enter your prompt: ").strip()

    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\nGoodbye!")
        break

    if not user_input:
        continue

    inputs = tokenizer(
        user_input,
        return_tensors="pt",
        max_length=MAX_INPUT_LENGTH,
        truncation=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=MAX_OUTPUT_LENGTH,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
                length_penalty=1.2
            )

        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\nGenerated:\n{result}\n")
    except Exception as e:
        print(f"\nAn error occurred during generation: {e}\n")
