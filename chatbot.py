from transformers import GPT2LMHeadModel, GPT2Tokenizer
from flask import Blueprint, request, session
import sqlite3
from dotenv import load_dotenv
import os
import logging

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

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
    data = request.get_json()
    message = data.get('message')
    logging.debug(f"Received message: {message}")
    if message:
        response = get_chatbot_response(message)
        logging.debug(f"Generated response: {response}")
        return {'response': response}
    logging.error("No message received")
    return {'response': 'No message received'}

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
    # Placeholder implementation
    return f"Chatbot response to: {message}"

def chatbot_response(user_input):
    # Placeholder implementation
    return f"Chatbot API response to: {user_input}"
