import requests
import json
import openai
import config
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_random_exponential
from datetime import datetime

# Ask GPT-3.5 Turbo
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10)) 
#To prevent API requests from timing out, gpt_request will retry max 10 times with intervals of 1-60 seconds
def gpt_request(query):
    
    """ Send a query to GPT-3.5 Turbo API and return the response """
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.gpt_api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages" : [{"role": "user", "content": query}],
        "max_tokens": 2000,
        "temperature": 0
    }

    response = requests.post(endpoint, headers=headers, json=data)
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()

# Search Google database
def google_request(claim):
    my_headers = config.my_headers
    endpoint = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'

    query = urllib.parse.quote(claim)
    language = 'en'
    max_days = 1000 #Max age of returned search results, in days
    page_size = 20 #Number of pages in the search results
    # reviewPublisherSiteFilter = '' #Filter by review publisher (can be blank)

    url = f'{endpoint}?query={query}&key={config.google_api_key}&languageCode={language}&maxAgeDays={max_days}&pageSize={page_size}'
    
    return url

# Process all tasks using sub-functions
def process(text):

    text = text.replace('\r\n', '').replace('\n', '').replace('\r', '') #delete new lines 
    print(f"Text: {text}")

    # GPT extracts search queries from input text
    query = f'As a journalist, extract the claims in the text below that might need to be fact-checked. Phrase them like search queries, including only important keywords that indicate contextual information, such as location, dates, or individuals involved and excluding any unnecessary words. From the output you return, each individual line, if input into a search engine, should give you any relevant information to prove or disprove the claim available online. ONLY return the claim, with each claim on a separate line. For example, if the input is "Donald Trump is responsible for the egg shortage and he denies Covid-19 ever existed", the output should be something like "Donald Trump egg shortage\nDonald Trump denies Covid-19 exists".\n\n{text}'
    
    queries = gpt_request(query).strip().split('\n')
    print(f"Queries: {queries}")

    # search Google's database
    links = [google_request(query) for query in queries]
    print(f"Links: {links}")


    # collect results we need
    results = []
    for link in links:
        my_headers = config.my_headers
        req = requests.get(link, headers=my_headers)
        print(f"Status code: {req.status_code}")
        data = req.json()
        print(f"Full data: {data}")
        if 'claims' in data:
            claims = data['claims'][:3]
            results.append(claims)
    print(f"Results: {results}") 


    # put publisher, verdict and url from in a list of tuples
    elements = [] 
    for nested_dict in results:
        factual_claim = nested_dict[0]['text']
        claim_review = nested_dict[0]['claimReview'][0]
        if 'reviewDate' in claim_review:
            review_date = claim_review['reviewDate']
            parsed_date = datetime.fromisoformat(review_date.rstrip("Z"))
            formatted_date = parsed_date.strftime("%B %d, %Y")
        else:
            formatted_date = 'Date not found'
        url = claim_review['url']
        verdict = claim_review.get('textualRating', 'No rating available')
        publisher = claim_review['publisher']['name']
        elements.append((factual_claim, publisher, verdict, url, formatted_date)) 
    elements = list(set(elements)) # delete duplicates
    print(f"Elements: {elements}") 

    # include all results in a list 
    answers = [f"We found {len(elements)} fact-check articles that may be relevant to the text you provided:"]
    for (factual_claim, publisher, verdict, url, formatted_date) in elements:
        answer = f"Claim: {factual_claim}<br>Review date: {formatted_date}<br>Verdict: {verdict}<br>Publisher: {publisher}<br>Link: <a href='{url}' target='_blank'>{url}</a>"
        answers.append(answer)
    print(f"Answers: {answers}")

    return answers