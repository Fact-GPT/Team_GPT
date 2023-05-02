gpt_api_key = #'<your OpenAI API key>'
my_headers = #{'User-Agent': '<your user agent>; <your email>. <your purpose for using the data>.'} You can find your user agent by simply searching for "my user agent" in Google.
google_api_key = #'<your Google Cloud API key>'
user_agent = #'<your user agent>; <your email>. <your purpose for using the data>.'

# Allow specific file extensions to be uploaded
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# Configure the maximum size of uploaded files (in bytes)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 megabytes

# Configure the directory where uploaded files will be saved
UPLOAD_FOLDER = #Create a sub-directory within the same directory as app.py, e.g. '/home/factgpt/Team_GPT/prototype/uploads'
