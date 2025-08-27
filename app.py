
import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')


# Simple in-memory user store: {username: password}
users = {}

# Set your Gemini API key here
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')  # Replace with your key or set as env var
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY

def ask_gemini(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "Sorry, I couldn't understand the response from Gemini."
    else:
        return f"Error: {response.status_code} - {response.text}"




# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            session['messages'] = []
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', signup=False, error=error)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            error = 'Username already exists.'
        else:
            users[username] = password
            session['username'] = username
            session['messages'] = []
            return redirect(url_for('index'))
    return render_template('login.html', signup=True, error=error)



# Main chat page (requires login)
@app.route('/', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'messages' not in session:
        session['messages'] = []
    return render_template('chat.html', messages=session['messages'])




@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_input = request.form['user_input']
    if 'messages' not in session:
        session['messages'] = []
    session['messages'].append(('user', user_input))
    bot_reply = ask_gemini(user_input)
    session['messages'].append(('bot', bot_reply))
    # Keep only the last 10 messages in session
    session['messages'] = session['messages'][-10:]
    session.modified = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
