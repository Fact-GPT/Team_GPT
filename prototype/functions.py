import requests
import json
import openai
import config
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_random_exponential
import newspaper
from newspaper import Article
from newspaper import Config

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


# Make a query using user input and ask GPT to decompose
def decompose(text): 
    
    """ Given a string of text, ask GPT-3.5-Turbo to summarise the claims made """
    
    query = "List out all of the claims made in the text below that might be contentious or need to be checked. \
    Exclude any source attribution or contact information unless relevant to verifying another fact. \
    Exclude names of people, using other identifying details, unless the name is crucial to the claim or they are famous. \
    Also exclude any subjective facts (such as thoughts, feelings or wishes) that cannot be independently verified. \
    List each claim as a brief bullet point, each independent and self-explanatory without reference to details from the rest of the text. \n\n"
    
    return gpt_request(query + text)


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


def scrape_article(url, user_agent=None):
    newspaper_config = Config()
    if user_agent:
        newspaper_config.browser_user_agent = user_agent
    newspaper_config.request_timeout = 10
    a = Article(url, config=newspaper_config, language='en')
    a.download()
    a.parse()
    return a.title + a.text[:10000]

# Summarise content using GPT-3.5 Turbo
def summarise_content(content):
    if content == 'NA':
        return "This website is not working"
    modified_content = f'Summarise the following content within 50 words: {content}'
    response = gpt_request(modified_content)
    return response

# Process all tasks using sub-functions
def process(text):
    claims = decompose(text)
    print("Claims identified: " + claims)
    if "\n" in claims:
        claims = claims.split("\n")

    optimised_claims = [gpt_request(f'Optimise the following claim to search for related information, focusing on the actors and general topic while avoiding overly specific details: {claim}') for claim in claims]

    print(f"Optimised claims: {optimised_claims}")

    links = [google_request(optimised_claim) for optimised_claim in optimised_claims]

    print(f"Links: {links}")

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

    elements = []
    for nested_list in results:
        for nested_dict in nested_list:
            factual_claim = nested_dict['text']
            for contained_dict in nested_dict['claimReview']:
                publisher = contained_dict['publisher']['name']
                url = contained_dict['url']
                verdict = contained_dict['textualRating']
                elements.append((factual_claim, publisher, verdict, url))

    print(f"Elements: {elements}") 

    contents = []
    for factual_claim, publisher, verdict, url in elements:
        if 'nytimes' in url:
            contents.append(scrape_article(url))
        elif 'verifythis' in url:
            contents.append('NA')
        else:
            contents.append(scrape_article(url, user_agent=config.user_agent))

    print(f"Contents: {contents}") 

    summaries = [summarise_content(content) for content in contents]

    print(f"Summaries: {summaries}") 

    data = []
    for i in range(len(elements)):
        factual_claim, publisher, verdict, url = elements[i]
        summary = summaries[i]
        data.append((factual_claim, publisher, verdict, url, summary))
    
    print(f"Data: {data}") 

    answers = [f"In the document you have provided, {len(data)} claims have been fact-checked before."]
    for (factual_claim, publisher, verdict, url, summary) in data:
        answer = f"Claim: {factual_claim}, <br>Fact-checker: {publisher}, <br>url: <a href='{url}'>{url}</a>, <br>summary: {summary}"
        answers.append(answer)

    print(f"Answers: {answers}") 
    return answers