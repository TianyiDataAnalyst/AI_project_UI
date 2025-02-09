from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the local directory to save the model and tokenizer
local_model_dir = "./local_model"

# Create the local_model directory if it does not exist
if not os.path.exists(local_model_dir):
    os.makedirs(local_model_dir)

# Check if the model and tokenizer are already downloaded
model_files_exist = os.path.exists(os.path.join(local_model_dir, "pytorch_model.bin"))
tokenizer_files_exist = os.path.exists(os.path.join(local_model_dir, "tokenizer.json"))

if not model_files_exist or not tokenizer_files_exist:
    logging.debug("Downloading GPT-2 model and tokenizer...")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model.save_pretrained(local_model_dir)
    tokenizer.save_pretrained(local_model_dir)
    logging.debug("GPT-2 model and tokenizer downloaded and saved to local directory.")
else:
    logging.debug("GPT-2 model and tokenizer already exist in the local directory.")
