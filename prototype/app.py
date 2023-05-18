from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import functions
from docx import Document
import pdfplumber
import git

app = Flask(__name__)
app.secret_key = os.urandom(24)

###PASSWORD PROTECTING###

# dictionary to store the username and hashed password pairs
users = {
    'gpt': generate_password_hash('FYjbvZeZN2qrFeVGtVwW')
}

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    return users.get(username)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        session['username'] = username
        return True
    return False

@app.errorhandler(401)
def unauthorized_handler(error):
    return 'Unauthorized access.', 401 

@app.route('/')
@auth.login_required
def example_page():
    return render_template('index.html')

####To automatically deploy python anywhere with every github push ####
@app.route('/git_update', methods=['POST'])
def git_update():
    repo = git.Repo('./Team_GPT')
    origin = repo.remotes.origin
    repo.create_head('main',
    origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
    origin.pull()
    return '', 200


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route('/process', methods=['GET', 'POST'])
def process():
    text = session.get('text', None)
    print("Retrieved text from session:", text)
    if text is not None:
        result = functions.process(text)
        session['result'] = result
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/loading', methods=['GET', 'POST'])
def loading():
    if request.method == "POST":
        try:
            print(request.form)
            # print(request.files)
            # For text input
            if "text_input" in request.form:
                text = request.form["text_input"]
                session['text'] = text
                print("Stored text in session:", text)
                return redirect(url_for('loading'))

        #    
        except Exception as e:
            print("Error:", e)
            return jsonify(success=False, error="Error processing text."), 400
        
    return render_template('loading.html', text=session.get('text', '')) 

@app.route('/results')
def results():
    result = session.get('result', None)
    if result is not None:
        return render_template('results.html', result=result)
    else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
