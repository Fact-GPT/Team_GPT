from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    # Do something with the file
    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)
