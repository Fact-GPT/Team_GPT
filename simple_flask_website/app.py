import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        query = request.form["query"]
        originator = request.form["originator"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(originator,query),
            temperature=0,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(originator,query):
    return """How true is this statement by {}? 
{}. 
ONLY reply using one of the following: 
1. True 
2. Partially true 
3. False
""".format(
        originator.title(), 
        query.capitalize()
    )
