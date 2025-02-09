from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import plotly
import plotly.express as px
import pandas as pd
import json

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Initialize database
def init_db():
    conn = sqlite3.connect('votes.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS votes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        option TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/project_description')
def project_description():
    return render_template('project_description.html')

@app.route('/algorithmic')
def algorithmic_trade():
    return render_template('algorithmic_trade.html')

@app.route('/project_description_internal')
def project_description_internal():
    return render_template('project_description_internal.html')

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

if __name__ == '__main__':
    init_db()
    from waitress import serve
    # Explicitly bind to all network interfaces
    serve(app, host='0.0.0.0', port=5000)