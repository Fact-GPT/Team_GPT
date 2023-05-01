import requests
import json
import openai
import config
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_random_exponential

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
    max_days = 365 #Max age of returned search results, in days
    page_size = 20 #Number of pages in the search results
    reviewPublisherSiteFilter = '' #Filter by review publisher (can be blank)

    url = f'{endpoint}?query={query}&key={config.google_api_key}&languageCode={language}&maxAgeDays={max_days}&pageSize={page_size}&reviewPublisherSiteFilter={reviewPublisherSiteFilter}'
    
    return url

# Process all tasks using sub-functions
def process(text):

    text = text.replace('\r\n', '').replace('\n', '').replace('\r', '') #delete new lines 
    print(f"Text: {text}")

    # GPT extracts keywords from input text
    query = f'Extract and list out all the keywords or sets of keywords from the text below \
    to search relevant article. List each claim as a brief bullet point. \n\n{text}'
    keywords = gpt_request(query).strip().split("\n")
    print(f"Keywords: {keywords}")


    # search Google's database
    links = [] 
    for keyword in keywords:
        link = google_request(keyword)
        links.append(link)
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
        url = claim_review['url']
        verdict = claim_review['textualRating']
        publisher = claim_review['publisher']['name']
        elements.append((factual_claim, publisher, verdict, url)) 
    elements = list(set(elements)) # delete duplicates
    print(f"Elements: {elements}") 

    # include all results in a list 
    answers = [f"We found {len(elements)} fact-check articles that may be relevant to the text you provided."]
    for (factual_claim, publisher, verdict, url) in elements:
        answer = f"Claim: {factual_claim}, <br>Fact-checker: {publisher}, <br>url: <a href='{url}' target='_blank'>{url}</a>"
        answers.append(answer)
    print(f"Answers: {answers}")

    return answers