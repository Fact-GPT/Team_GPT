The Checked-Fact Finder works following steps:

1. Read the text input, DOCX and PDF files provided by user.

2. Break the contents down into factual claims (Ask GPT-4).

3. Make those claims simple phrases (Ask GPT-4).

4. Search the database of Google Fact Check Explore's database using simplified claims as keywords (Fact Check Explore's).Results will be provided as a link or a set of links. If someone have checked and published the claim before, the details, such as date of fact checking, verdict(true or not), should be contained in the link in JSON format.

5. Picking claim, Fact Checker, and url of fact-checker's website up from the JSON file in the links.

6. Jump into the website and scrape contents (newspaper3k). Then summarise it (Ask GPT-4).

7. Display all sets of claim, Fact Checker, url and summary that fact-checkers have examined already. This suggests that incorrect information could be contained in the user input text or user uploaded files.   

You can demonstrate the functions using "sample.docx" and "sample.pdf" which are in the same project repository. There will be three results will be shown.

-----
Structure:
 The application has been build by Flask. 
 All functions above are in the "functions.py" file. The "app.py" file just import the functions from the "functions.py" file and implement them.
 This simple structure makes it more understandable for people to understand what is happening inside the app. 
 
-----
Future Development:
1. The application takes several minutes to show the result. This must be resolved because it is too long. Potential solutions are: 
- Development of GPT (GPT-4 works much slower than previous model "GPT-3.5-turbo.")
- Reduce the number of times that we ask GPT-4 to do something. Now we are asking 3 times to obtain the results. 
- Reduce stress while users waitng results by providing game.
(How about "joke generator?" It should be deployed easily because we have done exercise on the workshop in the fall semester.)

※Making a database that has results the app already searched before is not a good solution at the point when we provide the app to a small number of people.

2. To make results more readable, the results would be better to be displayed with original text. The best is highlighting applicable points and shows the results when users click it or hover on there.

3. The Google's database might not have sufficient amout of data (most users might get no reult.) We should think to provide alternative information instead of just telling "no results." 
- Deploying extension function for web browser will increase the chance to see this app working.

4. Some important private information are exposed to the world. API_keys, user_agent and my_header should be kept secret.

5. Also, we should consider how we can operate this app without our personal keys. 

6. User interface should be improved to help users.

7. If we take this project more realistic, we must think about the method for collecting money from users.

8. It doesn't always respond the same result for the same document.





