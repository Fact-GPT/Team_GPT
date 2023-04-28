The fact-check review finder does the following:

1. Read the text input, DOCX and PDF files provided by a user.

2. Extract keywords or sets of keywords using GPT-3.5-Turbo.

3. Search the Google Fact Check Explore's database using keywords. Results will be provided as a link or a set of links. It should contain the details of fact check review, such as url and verdict(true or false) in the JSON format.

4. Collecting claim, Fact Checker, and url of fact-checker's website up from the links.

5. Display them.   

(You can demonstrate the applications using "sample.docx" and "sample.pdf" those are in the same project repository.)

-----
Structure:
 The application has been build by Flask. 
 Most functions above are programmed in the "functions.py" file. The "app.py" file reads the text input or uploaded by the users. Then it imports the functions from the "functions.py" and implement them.
 
 The core functions are calling API of both GPT-3.5-turbo and Google's database. GPT has the latest API model of "GPT-4", but it needs long time to execute. Therefore, we selected GPT-3.5-turbo for the app.
 
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





