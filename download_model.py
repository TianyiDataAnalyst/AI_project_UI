
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os

# Define the directory where the model will be saved
local_model_dir = "./local_model"

# Create the directory if it doesn't exist
os.makedirs(local_model_dir, exist_ok=True)

# Download the GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Save model and tokenizer to the local directory
model.save_pretrained(local_model_dir)
tokenizer.save_pretrained(local_model_dir)

print(f"GPT-2 model and tokenizer have been saved to {local_model_dir}")