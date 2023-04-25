import requests
import json
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
import newspaper
from newspaper import Article
from newspaper import Config

# Ask GPT-4
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10)) 
#To prevent API requests from timing out, gpt_request will retry max 10 times with intervals of 1-60 seconds
def gpt_request(query):
    
    """ Send a query to GPT-4 API and return the response """
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    api_key = "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"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4",
        "messages" : [{"role": "user", "content": query}],
        "max_tokens": 2000,
        "temperature": 0
    }

    response = requests.post(endpoint, headers=headers, json=data)
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()


# Make a query using user input and ask GPT to decompose
def decompose(text): 
    
    """ Given a string of text, ask GPT-4 to summarise the claims made """
    
    query = "List out all of the claims made in the text below that might be contentious or need to be checked. \
    Exclude any source attribution or contact information unless relevant to verifying another fact. \
    Exclude names of people, using other identifying details, unless the name is crucial to the claim or they are famous. \
    Also exclude any subjective facts (such as thoughts, feelings or wishes) that cannot be independently verified. \
    List each claim as a brief bullet point, each independent and self-explanatory without reference to details from the rest of the text. \n\n"
    
    return gpt_request(query + text)


# Search Google database
def google_request(claim):
    # Melissa's header
    # my_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36; Melissa Zhu/ZhuM17@cardiff.ac.uk. Working on data for class.'}
    # Koh's header
    my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56; Koh Yoshida/yoshidak1@cardiff.ac.uk. Working on data for class.'} 
    endpoint = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'

    query = claim
    language = 'en'
    max_days = 10000 #Max age of returned search results, in days
    page_size = 20 #Number of pages in the search results
    reviewPublisherSiteFilter = '' #Filter by review publisher (can be blank)

  # api_key = 'AIzaSyDKpe6j4lqR_yuy6FZMI3NEdY9VP7Fa2jI' # Melissa's key
    api_key = 'AIzaSyAAB8N8l47u7kt_EfrPFUKpwfOPYRmIlGw' # Koh's key

    url = f'{endpoint}?query={query}&key={api_key}&languageCode={language}&maxAgeDays={max_days}&pageSize={page_size}&reviewPublisherSiteFilter={reviewPublisherSiteFilter}'
    
    return url


# Scraping (newspaper3k) documentation: https://newspaper.readthedocs.io/en/latest/
# We use two funtions below for scraping
def scraping_with_none(url):
    a = Article(url, language='en') 
    a.download()
    a.parse()
    return (a.title + a.text[:10000])

def scraping_with_UserAgent(url):
    # Koh's user_agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56; Koh Yoshida/yoshidak1@cardiff.ac.uk. Collecting content for group project in my class.'
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10 # avoid runtime error
    a = Article(url, config=config, language='en') 
    a.download()
    a.parse()
    return (a.title + a.text[:10000])    


# Process all tasks using sub-functions above
def process(text):

    claims = decompose(text) # ask GPT to decompse original user input and make a list of factual claims
    if "\n" in claims:
        claims = claims.split("\n")
        
    modified_claims = [] # add conditions to factual claims for the next step (ask GPT again)
    for claim in claims:
        new_claim = 'Optimise the following claim to search for related information, focusing on the actors and general topic while avoiding overly specific details: ' + claim
        modified_claims.append(new_claim)
        
    optimised_claims = [] # ask GPT to optimise factual claims to be searched 
    for modified_claim in modified_claims:
        response = gpt_request(modified_claim)
        optimised_claims.append(response)
    
    links = [] # search Google's database and make a list of answer urls
    for optimised_claim in optimised_claims:
        link = google_request(optimised_claim)
        links.append(link)
    
    results = [] # capture the details of search result
    for link in links:
        # Koh's header
        my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56; Koh Yoshida/yoshidak1@cardiff.ac.uk. Working on data for class.'}
        req = requests.get(link, headers = my_headers)
        data = req.json()
        if 'claims' in data: 
            claims = data['claims']
            results.append(claims)
    for result in results: 
        if len(result) > 3:  #limit to max 3 results/query for brevity
            result = result[:3]
    
    elements = [] # extract publisher name, verdict and url from result as a list of tuples
    for nested_list in results:
        for nested_dict in nested_list:
            factual_claim = nested_dict['text']
            for contained_dict in nested_dict['claimReview']:
                publisher = contained_dict['publisher']['name']
                url = contained_dict['url']
                verdict = contained_dict['textualRating']
                elements.append((factual_claim, publisher, verdict, url))    
    
    contents = [] # scraping urls using newspaper3k
    for factual_claim, publisher, verdict, url in elements:
        if 'nytimes' in url:
            contents.append(scraping_with_none(url))
        elif 'verifythis' in url:
            contents.append('NA') # Exception as "Verifythis.com" is not accessible in the UK
        else:
            contents.append(scraping_with_UserAgent(url))
     
    summaries = [] # ask GPT to summarise contents that have been scraped  
    for content in contents:
        if content == 'NA':
            summaries.append("This website is not working")
        else: 
            modified_content = f'Summarise the following content within 50 words: {content}'
            response = gpt_request(modified_content)
            summaries.append(response)

    # add summary to the list of tuples that contains publishers, verdicts and urls
    data = []
    for i in range(len(elements)):
        factual_claim, publisher, verdict, url = elements[i]
        summary = summaries[i]
        data.append((factual_claim, publisher, verdict, url, summary))
    
    # include all results in a list 
    answers = [f"In the document you have provided, {len(data)} factors have been fact-checked before."]
    for (factual_claim, publisher, verdict, url, summary) in data:
        answer = f"Factor: {factual_claim}, <br>Fact-checker: {publisher}, <br>url: <a href='{url}'>{url}</a>, <br>summary: {summary}"
        answers.append(answer)
        
    return answers