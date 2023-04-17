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

    processed_data = process_claims(claims)

    output = {
            "original_text": text,
            "claims": claims,
            "highlighted_text": highlighted_text
            "fact_check_reviews": summaries
        }
    
    return jsonify(output)

def process_claims(optimised_queries): 
    my_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36; Melissa Zhu/ZhuM17@cardiff.ac.uk. Working on data for class.'}

    endpoint = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'

    links = []

    for optimised_query in optimised_queries:
        
        query = optimised_query
        language = 'en'
        max_days = 10000 #Max age of returned search results, in days
        page_size = 20 #Number of pages in the search results

        reviewPublisherSiteFilter = '' #Filter by review publisher (can be blank)

        api_key = 'AIzaSyDKpe6j4lqR_yuy6FZMI3NEdY9VP7Fa2jI' # Melissa's key

        url = f'{endpoint}?query={query}&key={api_key}&languageCode={language}&maxAgeDays={max_days}&pageSize={page_size}&reviewPublisherSiteFilter={reviewPublisherSiteFilter}'
        links.append(url)

        results = []
        for link in links:
            req = requests.get(link, headers = my_headers)
            data = req.json()
            if 'claims' in data: 
                claims = data['claims']
                results.append(claims)
                
        for result in results: 
            if len(result) > 3:  #Limit to max 3 results/query for brevity
                result = result[:3]

        search_queries = []
        claims = []
        originators = []
        claim_dates = []
        reviews = []
        publisher_names = []
        publisher_sites = []
        review_urls = []
        titles = []
        review_dates = []
        ratings = []

        for i in range(len(results)): 
            search_query = optimised_queries[i] #Match queries to results
            search_queries += len(results[i]) * [search_query]

        for result in results: 
            for i in range(len(result)):
                claim = result[i]['text']
                claims.append(claim)

        for result in results: 
            for i in range(len(result)):
                if 'claimant' in result[i]:
                    originator = result[i]['claimant']
                    originators.append(originator)
                else: 
                    originators.append('NA')

        for result in results: 
            for i in range(len(result)):
                if 'claimDate' in result[i]:
                    date = result[i]['claimDate']
                    claim_dates.append(date)
                else: 
                    claim_dates.append('NA')

        for result in results: 
            for i in range(len(result)):
                first_review = result[i]['claimReview'][0]
                reviews.append(first_review) #Most only have one review but some of them have many reviews all saying the same thing so gonna keep it to one to standardise the dataframe

        for review in reviews: 
            if 'publisher' in review and 'name' in review['publisher']: 
                publisher_name = review['publisher']['name']
                publisher_names.append(publisher_name)
            else: 
                publisher_names.append('NA')

        for review in reviews: 
            if 'publisher' in review and 'site' in review['publisher']: 
                publisher_site = review['publisher']['site']
                publisher_sites.append(publisher_site)
            else: 
                publisher_sites.append('NA')

        for review in reviews: 
            if 'url' in review: 
                review_url = review['url']
                review_urls.append(review_url)
            else: 
                review_urls.append('NA')
                
        for review in reviews: 
            if 'title' in review: 
                title = review['title']
                titles.append(title)
            else: 
                titles.append('NA')

        for review in reviews: 
            if 'reviewDate' in review: 
                review_date = review['reviewDate']
                review_dates.append(review_date)
            else: 
                review_dates.append('NA')

        for review in reviews: 
            if 'textualRating' in review: 
                rating = review['textualRating']
                ratings.append(rating)
            else: 
                ratings.append('NA')

        df = pd.DataFrame({'query': search_queries,
                        'claim': claims, 
                        'originator': originators, 
                        'claim_date': claim_dates, 
                        'review_publisher': publisher_names, 
                        'publisher_site': publisher_sites, 
                        'review_url': review_urls, 
                        'review_title': titles, 
                        'review_date': review_dates, 
                        'verdict': ratings})
        
    return df

    if __name__ == "__main__":
        app.run()

