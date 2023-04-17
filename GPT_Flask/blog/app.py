import os
import openai
from flask import Flask, redirect, request, jsonify, render_template, url_for
import requests
import json
import random 
import numpy
import pandas as pd
from datetime import date
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
import newspaper
from newspaper import Article
from newspaper import Config

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

#Defining functions for querying gpt and summarising claims

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10)) 
#To prevent API requests from timing out, gpt_request will retry max 10 times with intervals of 1-60 seconds

def gpt_request(query):
    
    """ Send a query to GPT-4 API and return the response """
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    api_key = "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"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    data = {
        "model": "gpt-4",
        # We don't need system message cos we don't ask fact checking
        "messages" : [{"role": "user", "content": query}],
        "max_tokens": 2000,
        "temperature": 0
    }

    response = requests.post(endpoint, headers=headers, json=data)
    response_json = response.json()
    # print(response_json)
    return response_json['choices'][0]['message']['content'].strip()

def summarise(text): 
    
    """ Given a string of text, ask GPT-4 to summarise the claims made """
    
    query = "List out all of the claims made in the text below that might be contentious or need to be checked. \
    Exclude any source attribution or contact information unless relevant to verifying another fact. \
    Exclude names of people, using other identifying details, unless the name is crucial to the claim or they are famous. \
    Also exclude any subjective facts (such as thoughts, feelings or wishes) that cannot be independently verified. \
    List each claim as a brief bullet point, each independent and self-explanatory without reference to details from the rest of the text. \n\n"
    
    return gpt_request(query + text)
    

# APP ROUTES

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/process_text", methods=["POST"])
def process_text(): 
    text = request.form["text"]
    claims = summarise(text)
    if "\n" in claims:
        claims = claims.split("\n")

    modified_queries = []
    for claim in claims:
        new_query = 'Optimise the following claim to search for related information, focusing on the actors and general topic while avoiding overly specific details: ' + claim
        modified_queries.append(new_query)
    
    optimised_queries = []
    for query in modified_queries:
        response = gpt_request(query)
        optimised_queries.append(response)
    
    output = {
        "original_text": text,
        "claims": claims,
        "fact_check_reviews": summaries
    }
    
    return jsonify(output)

    if __name__ == "__main__":
        app.run()

