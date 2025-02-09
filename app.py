from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
import sqlite3
import plotly
import plotly.express as px
import pandas as pd
import json
import os
from chatbot import chatbot_bp, get_chatbot_response, chatbot_response, get_answer_from_model
from dotenv import load_dotenv
import logging

load_dotenv()

# Enable logging
logging.basicConfig(level=logging.DEBUG)

try:
    from transformers import GPT2Tokenizer, GPT2LMHeadModel
    # Specify the cache directory if necessary
    cache_dir = os.getenv('TRANSFORMERS_CACHE', default=None)
    # Attempt to load the model and tokenizer
    GPT2Tokenizer.from_pretrained("gpt2", cache_dir=cache_dir)
    GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=cache_dir)
except Exception as e:
    logging.error("GPT-2 model and tokenizer not found in the local directory. Please run download_model.py to download them.")
    raise e

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY')

# Register chatbot routes
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

# Initialize database
def init_db():
    conn = sqlite3.connect('votes.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS votes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        option TEXT)''')
    conn.commit()
    conn.close()

# Initialize user database
def init_user_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()
    conn.close()

# Initialize the databases
init_db()
init_user_db()

@app.route('/project_description')
def project_description():
    return render_template('project_description.html')

@app.route('/algorithmic')
def algorithmic_trade():
    return render_template('algorithmic_trade.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('view_facts'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/view_facts')
def view_facts():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('view_facts.html')

@app.route('/facts')
def facts():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('facts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM facts")
    facts = cursor.fetchall()
    conn.close()
    return jsonify({'facts': [{'question': fact[0], 'answer': fact[1]} for fact in facts]})

@app.route('/export_facts')
def export_facts():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('facts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM facts")
    facts = cursor.fetchall()
    conn.close()
    with open('facts.txt', 'w') as f:
        for fact in facts:
            f.write(f"{fact[0]}: {fact[1]}\n")
    return send_file('facts.txt', as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot')
def plot():
    try:
        conn = sqlite3.connect('votes.db')
        query = "SELECT option, COUNT(*) as count FROM votes GROUP BY option"
        df = pd.read_sql_query(query, conn)
        conn.close()

        fig = px.bar(df, x='option', y='count', title='Vote Results')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return graphJSON
    except Exception as e:
        print(f"Error generating plot: {e}")
        return "Error generating plot", 500

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        selected_option = request.form.get('option')
        if not selected_option:
            return 'No option selected', 400
        
        try:
            conn = sqlite3.connect('votes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO votes (option) VALUES (?)", (selected_option,))
            conn.commit()
            conn.close()
            return redirect(url_for('vote'))
        except Exception as e:
            print(f"Database error: {e}")
            return 'Error saving vote', 500

    # GET request handling
    try:
        conn = sqlite3.connect('votes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT option, COUNT(*) FROM votes GROUP BY option")
        results = cursor.fetchall()
        conn.close()
        return render_template('vote.html', results=results)
    except Exception as e:
        print(f"Database error: {e}")
        return 'Error fetching results', 500
 
@app.route('/reset_votes', methods=['POST'])
def reset_votes():
    try:
        conn = sqlite3.connect('votes.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM votes")
        conn.commit()
        conn.close()
        return redirect(url_for('vote'))
    except Exception as e:
        print(f"Error resetting votes: {e}")
        return "Error resetting votes", 500   

@app.route('/enterprise_prebuilt_applications')
def enterprise_prebuilt_applications():
    return render_template('enterprise_prebuilt_applications.html')

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_message = request.form.get('message')
        if not user_message:
            return 'No message provided', 400
        
        try:
            bot_response = get_chatbot_response(user_message)
            return jsonify({'response': bot_response})
        except Exception as e:
            print(f"Error in chatbot response: {e}")
            return 'Error processing message', 500

    return render_template('chatbot.html')

@app.route('/chatbot_api', methods=['POST'])
def chatbot_api():
    user_input = request.json.get('user_input')
    response = chatbot_response(user_input)
    return jsonify({'response': response})

@app.route('/ask', methods=['POST'])
def ask_question():
    user_login_id = session.get('user_login_id')
    question = request.form['question']
    answer = get_answer_from_model(question)
    
    conn = sqlite3.connect('facts.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO facts (question, answer, user_login_id) VALUES (?, ?, ?)', (question, answer, user_login_id))
    conn.commit()
    conn.close()
    
    return {'question': question, 'answer': answer}

if __name__ == '__main__':
    init_db()
    init_user_db()
    # Explicitly bind to all network interfaces
    app.run(
        host='0.0.0.0',  # Bind to all interfaces
        port=5000,
        debug=True,
        use_reloader=True
    )