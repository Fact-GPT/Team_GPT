** Fact-GPT: Fact-check review finder **

---

// Project description //

This project, by students in Cardiff University's 2022/2023 MSc Computational and Data Journalism programme cohort, is an experimental fact-checking tool using generative AI. It was built with journalists in mind, although it may have uses for broader audiences including media-literate news consumers who wish to ensure that the articles they read are likely to be accurate.


The fact-check review finder does the following:

1. Takes text input from a user

2. Identifies claims that might need fact-checking and extracts keywords relevant to these using OpenAI's GPT-3.5-Turbo model

3.Inputs these keywords as queries in a database of fact checking articles using Google's Fact Check Tools API: https://developers.google.com/fact-check/tools/api 

4. Returns a list of claims that might need to be fact-checked, as well as any fact check articles (including the claim checked, date, verdict, publisher and URL) that may be relevant to claims identified in the text

Generative AI is currently unreliable in fact-checking claims by itself. However, as a language model it has potential in understanding what claims may look like. We aim to combine this potential with Google Fact Check Tools' database of actual reviews of claims by legitimate organisations such as AFP Fact Check, PolitiFact and Full Fact, to help journalists detect any claims in source material that may already have been debunked without having to manually search for each claim themselves.

The latest version of the app is currently hosted at http://factgpt.pythonanywhere.com.

---

// How to run this code //

- Download ALL files onto local drive 

- You will need API keys for both OpenAI and Google Cloud. More information on how to get API keys for these services can be found at https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key and https://support.google.com/googleapi/answer/6158862 respectively.

- Follow the instructions to fill in your custom details in "config_TEMPLATE.py", and rename it "config.py". 

- Run app.py on a Flask server through your terminal 

-----

// Future development //


OpenAI released a newer GPT-4 model on a limited basis on 14 March, 2023. Although this model is said to be superior in many ways, including being able to understand more context, we have also found that API calls take longer which could affect the user experience significantly. We have therefore opted to use GPT-3.5-Turbo until GPT-4 is rolled out more widely and can return responses at a comparably fast rate. 

We are looking to refine the prompts to further improve the consistency, accuracy and relevance of results. 

Rather than simply listing potentially related fact checks, we want to work towards returning a summary of their contents. Currently, the time taken to scrape the content of the articles and summarise them is too long and may affect the user experience. 

Currently the tool can only detect fact check articles in English. More languages may be added in the future. 

In the longer term, this programme could be made into a plug-in for browsers or text editors, which highlights potential claims and relevant fact-checks in real-time. 



