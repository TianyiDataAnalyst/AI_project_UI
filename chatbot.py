from transformers import GPT2LMHeadModel, GPT2Tokenizer
from flask import Blueprint, request, session
import sqlite3
from dotenv import load_dotenv
import os
import logging
import torch

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the local directory to save the model and tokenizer
local_model_dir = "./local_model"

# Check if the model and tokenizer are already downloaded
model_files_exist = os.path.exists(os.path.join(local_model_dir, "pytorch_model.bin"))
tokenizer_files_exist = os.path.exists(os.path.join(local_model_dir, "tokenizer.json"))

if not model_files_exist or not tokenizer_files_exist:
    logging.error("GPT-2 model and tokenizer not found in the local directory. Please run download_model.py to download them.")
    raise FileNotFoundError("GPT-2 model and tokenizer not found in the local directory.")
else:
    logging.debug("Loading GPT-2 model and tokenizer from local directory...")
    model = GPT2LMHeadModel.from_pretrained(local_model_dir, local_files_only=True)
    tokenizer = GPT2Tokenizer.from_pretrained(local_model_dir, local_files_only=True)

# Set the model in evaluation mode
model.eval()

def get_fact_answer(question):
    connection = sqlite3.connect('facts.db')
    cursor = connection.cursor()
    cursor.execute("SELECT answer FROM facts WHERE question LIKE ?", ('%' + question + '%',))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        return None

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot_route():
    try:
        data = request.get_json()
        logging.debug(f"Received data: {data}")
        message = data.get('message')
        logging.debug(f"Received message: {message}")
        if message:
            response = get_chatbot_response(message)
            logging.debug(f"Generated response: {response}")
            return {'response': response}
        logging.error("No message received")
        return {'response': 'No message received'}, 400
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return {'response': 'Error processing request'}, 500

def get_answer_from_model(question):
    fact_answer = get_fact_answer(question)
    if fact_answer:
        return fact_answer
    else:
        inputs = tokenizer(question, return_tensors="pt")
        outputs = model.generate(**inputs)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.debug(f"Model output: {response}")
        return response

def get_chatbot_response(message):
    return chat_with_gpt2(message)

def chatbot_response(user_input):
    return chat_with_gpt2(user_input)

def chat_with_gpt2(input_text):
    # Encode the input text to get token IDs
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # Generate a response from GPT-2
    with torch.no_grad():
        output = model.generate(input_ids, max_length=100, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)

    # Decode the generated tokens to text
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response
