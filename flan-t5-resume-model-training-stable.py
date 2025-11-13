
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import json
import torch

try:
    from transformers import (
        T5Tokenizer,
        T5ForConditionalGeneration,
        Trainer,
        TrainingArguments,
        DataCollatorForSeq2Seq
    )
    from datasets import Dataset
except Exception as e:
    print("\n" + "="*70)
    print("ERROR: Missing libraries. Run this first:")
    print("!pip install --upgrade transformers datasets torch accelerate sentencepiece")
    print("Then restart runtime and re-run this cell.")
    print("="*70)
    raise

print("="*70)
print("T5 Resume Fine-Tuning Script (Stable)")
print("Optimized for Google Colab Free Tier")
print("="*70)

# for gpu
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n✓ Using device: {device}")
if device == "cuda":
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

torch.autograd.set_detect_anomaly(False)


# config and model loading
MODEL_NAME = "google/t5v1_1"       #chosen because the most stable after repeated training 
OUTPUT_DIR = "./flan-t5-base-resume-finetuned-stable"
BATCH_SIZE = 2
MAX_INPUT_LENGTH = 128
MAX_OUTPUT_LENGTH = 256
LEARNING_RATE = 2e-4  # safer and more stable

print(f"\n⚙️  MODEL: {MODEL_NAME}")
print(f"✓ Max input length: {MAX_INPUT_LENGTH} tokens")
print(f"✓ Max output length: {MAX_OUTPUT_LENGTH} tokens")

# ------------------------------------------------------------
# LOAD DATASETS
# ------------------------------------------------------------
print("\n" + "-"*70)
print("Loading dataset...")
print("-"*70)

with open("train_data.json", "r") as f:
    train_data = json.load(f)
with open("val_data.json", "r") as f:
    val_data = json.load(f)

print(f"✓ Training examples: {len(train_data)}")
print(f"✓ Validation examples: {len(val_data)}")

# ------------------------------------------------------------
# LOAD MODEL & TOKENIZER
# ------------------------------------------------------------
print("\n" + "-"*70)
print("Loading model and tokenizer...")
print("-"*70)

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

print(f"✓ Model parameters: {model.num_parameters() / 1e6:.1f}M")

# ------------------------------------------------------------
# TOKENIZATION FUNCTION
# ------------------------------------------------------------
def preprocess_function(examples):
    inputs = examples["input"]
    targets = examples["output"]

    model_inputs = tokenizer(
        inputs,
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
        padding=False
    )

    labels = tokenizer(
        targets,
        max_length=MAX_OUTPUT_LENGTH,
        truncation=True,
        padding=False
    )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

train_dataset = Dataset.from_list(train_data)
val_dataset = Dataset.from_list(val_data)

print("\n" + "-"*70)
print("Tokenizing dataset...")
print("-"*70)

train_dataset = train_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=["input", "output"]
)
val_dataset = val_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=["input", "output"]
)

print("✓ Tokenization complete")

# ------------------------------------------------------------
# DATA COLLATOR
# ------------------------------------------------------------
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True
)

# ------------------------------------------------------------
# TRAINING CONFIGURATION (Safe FP32 Mode)
# ------------------------------------------------------------
print("\n" + "-"*70)
print("Configuring training (FP32 safe mode)...")
print("-"*70)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    num_train_epochs=8,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE * 2,
    gradient_accumulation_steps=8 // BATCH_SIZE,  # effective batch size = 8

    learning_rate=LEARNING_RATE,
    warmup_steps=100,
    weight_decay=0.01,
    max_grad_norm=1.0,

    fp16=False,  # <--- Disabled FP16 to fix NaN loss
    fp16_full_eval=False,

    eval_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_total_limit=3,

    logging_steps=50,
    logging_dir="./logs",
    logging_first_step=True,

    gradient_checkpointing=True,
    optim="adafactor",

    dataloader_num_workers=0,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,

    report_to="none",
    push_to_hub=False,
    seed=42,
)

print("Training Configuration:")
print(f"  • Model: {MODEL_NAME}")
print(f"  • Learning rate: {LEARNING_RATE}")
print(f"  • FP16: {training_args.fp16} (disabled for stability)")
print(f"  • Batch size: {training_args.per_device_train_batch_size}")
print(f"  • Gradient accumulation: {training_args.gradient_accumulation_steps}")

# ------------------------------------------------------------
# TRAINING
# ------------------------------------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("\n" + "="*70)
print("Starting training (FP32 mode)...")
print("="*70)
print("\nTip: Checkpoints will save every 100 steps.\n")

try:
    trainer.train()
    print("\n" + "="*70)
    print("✓ Training completed successfully!")
    print("="*70)
except KeyboardInterrupt:
    print("\nTraining interrupted by user. Checkpoint saved.")
except Exception as e:
    print("\n⚠ Training stopped due to error:")
    print(e)
    print("You can resume from the last checkpoint by re-running trainer.train().")

# ------------------------------------------------------------
# SAVE MODEL
# ------------------------------------------------------------
print("\n" + "-"*70)
print("Saving final model...")
print("-"*70)

final_dir = f"{OUTPUT_DIR}/final_model"
model.save_pretrained(final_dir)
tokenizer.save_pretrained(final_dir)
print(f"✓ Model saved to: {final_dir}")
# evalutaing the model
print("\n" + "-"*70)
print("Running final evaluation...")
print("-"*70)

eval_results = trainer.evaluate()
print("\nValidation Results:")
for key, value in eval_results.items():
    print(f"  • {key}: {value:.4f}")

final_loss = eval_results.get('eval_loss', 999)
print("\n" + "="*70)
print("Training Quality Assessment:")
print("="*70)
if final_loss < 0.5:
    print("✓ EXCELLENT: Model trained very well (loss < 0.5)")
elif final_loss < 1.0:
    print("✓ GOOD: Model trained well (loss < 1.0)")
elif final_loss < 1.5:
    print("⚠ FAIR: Somewhat trained (loss < 1.5)")
else:
    print("❌ POOR: Model may need more epochs or tuning.")
print(f"\nFinal validation loss: {final_loss:.4f}")
print("="*70)

# Testing the Model
print("\n" + "-"*70)
print("Quick Test Inference:")
print("-"*70)

test_input = "Rewrite professionally: Built web applications using Python"
inputs = tokenizer(test_input, return_tensors="pt", max_length=MAX_INPUT_LENGTH, truncation=True)
inputs = {k: v.to(device) for k, v in inputs.items()}

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_length=MAX_OUTPUT_LENGTH,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3
    )

result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"\nInput: {test_input}")
print(f"Output: {result}")

print("\n✓ All done! Your fine-tuned model is ready (FP32 stable mode).")
