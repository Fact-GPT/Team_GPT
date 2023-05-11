import requests
import ast
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
        "max_tokens": 3000,
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
    page_size = 2 #Number of pages in the search results
    # reviewPublisherSiteFilter = '' #Filter by review publisher (can be blank)

    url = f'{endpoint}?query={query}&key={config.google_api_key}&languageCode={language}&maxAgeDays={max_days}&pageSize={page_size}'
    
    return url

# Process all tasks using sub-functions
def process(text):

    text = text.replace('\r\n', '').replace('\n', '').replace('\r', '') #delete new lines 
    print(f"Text: {text}")

    # GPT extracts search queries from input text
    query = f"As a journalist, extract the claims in the text below that might need to be fact-checked. For each claim, return a tuple with two parts: the first is the claim, and the second is a list of three possible search queries that should give you any available information online to prove or disprove the claim. The search queries should include important keywords that indicate contextual information, such as location, dates, or individuals involved, and use language that aligns with the claims made in the text. All the strings in the tuples should be enclosed in DOUBLE quotation marks. For example, if the input is \"Donald Trump is responsible for the egg shortage and he denies Covid-19 ever existed\", there are two claims, so the output should be something like:[(\"Donald Trump is responsible for the egg shortage\", [\"Donald Trump caused egg shortage?\", \"Donald Trump egg prices\", \"Trump administration egg shortage\"]),(\"Donald Trump denies Covid-19 ever existed\", [\"Donald Trump claims Covid-19 is a hoax\", \"Trump denies existence of Covid-19\", \"Trump administration and Covid-19 denial\"])]. ONLY return responses in a list of tuples, without any other output even if you think that the claims are unlikely to be true. \n\n{text}"

    try:
        responses = gpt_request(query).strip()
        responses = responses.replace('\n', '')
        print(f"Responses: {responses}. Type: {type(responses)}")
        claims_with_queries = ast.literal_eval(responses)
    except Exception as e:
        # Handle the exception here
        print(f"An error occurred: response was not in the format expected")
        claims_with_queries = []


    # Search Google's database and collect results if there were any claims identified
    all_results = {}
    for claim, queries in claims_with_queries:
        claim_results = []
        for query in queries:
            url = google_request(query)
            my_headers = config.my_headers
            req = requests.get(url, headers=my_headers)
            print(f"Status code: {req.status_code}")
            data = req.json()
            print(f"Full data: {data}")
            if 'claims' in data:
                claims = data['claims'][:3]
                claim_results.extend(claims)
        all_results[claim] = claim_results
        print(f"All results: {all_results}")


    # put publisher, verdict and url from in a list of tuples
    final_results = {}
    for claim, results in all_results.items():
        elements = [] 
        if results:
            for claim_dict in results: 
                factual_claim = claim_dict['text']
                claim_review = claim_dict['claimReview'][0]
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
        print(f"Elements for '{claim}': {elements}") 
        final_results[claim] = elements

    # include all results in a list 
    if len(final_results) == 0: 
        answers = [f"We could not detect any claims that might need to be fact-checked in the text you provided. However, you may still want to verify any claims you find suspicious on other platforms."]
    else: 
        answers = [f"There were <b>{len(final_results)}</b> claims detected in the text you submitted that might need fact-checking."]
        for claim, elements in final_results.items():
            if len(elements) == 0:
                answers.append(f"<b>'{claim}'</b> was identified in the text as a statement that might need fact-checking, but no related fact-check articles have been found. Nonetheless, you may have to verify this claim. For more information on the articles included in this search, please refer to <a href='https://toolbox.google.com/factcheck/about#fcmt-claimreview' target='_blank'>Google Fact Check Tools</a>.")
            else:
                answers.append(f"Claim: {claim}")
                answers.append("Possibly related fact-checks:")
                for (factual_claim, publisher, verdict, url, formatted_date) in elements:
                    answer = f"Fact-checked claim: {factual_claim}<br>Review date: {formatted_date}<br>Verdict: {verdict}<br>Publisher: <a href='{url}' target='_blank'>{publisher}</a>"
                    answers.append(answer)

    print(f"Answers: {answers}")

    return answers