from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

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

@app.route('/enterprise_prebuilt_applications')
def enterprise_prebuilt_applications():
    return render_template('enterprise_prebuilt_applications.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)