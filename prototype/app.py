from flask import Flask, request, render_template, redirect, url_for
import os
import functions
from docx import Document
import pdfplumber

app = Flask(__name__)

# setting file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def read_docx(filepath):
    doc = Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf(filepath):
    with pdfplumber.open(filepath) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def read_doc(filepath):
    # change the format of doc file into docx file to read
    import subprocess
    import tempfile
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp_filename = temp.name
    temp.close()
    subprocess.call(["soffice", "--headless", "--convert-to", "docx", "--outdir", tempfile.gettempdir(), filepath])
    docx_filename = os.path.splitext(filepath)[0] + '.docx'
    temp_docx_filename = os.path.join(tempfile.gettempdir(), docx_filename)
    text = read_docx(temp_docx_filename)
    os.remove(temp_docx_filename)
    return text

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # In case text input
        if "text_input" in request.form:
            text = request.form["text_input"]
            result = functions.process(text)
            return render_template("results.html", result=result)
        
        # In case uploading file
        if "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext == 'docx':
                    text = read_docx(filepath)
                elif file_ext == 'pdf':
                    text = read_pdf(filepath)
                elif file_ext == 'doc':
                    text = read_doc(filepath)
                else:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                os.remove(filepath)  # delete file
                result = functions.process(text)
                return render_template("results.html", result=result)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)