# news-translator-summarizer-player
A simplistic news service that extracts news from a foreign news portal (in a foreign language), translates to english, summarizes the content and then speaks out the summary at a given time of day after doing a sentiment analysis on it. It then stores the summarized news article categorized based on sentiment (positive, negative or neutral) for later viewing (where the user can choose the sentiment of the news they want to view - refer to the screen shot below Step 5).

Prerequisites

    (a) Make sure you have a virtual python environment with python 3.9
        % conda create -n <news_player_env> python=3.9
        
    (b) Activate the new virtual environment and install the needed packages
        % conda activate <news_player_env>
        % pip install -r requirements.txt
    

Step 1 :
    Create a cognitive service instance and a language resource instance in the azure portal
        https://portal.azure.com
        
Step 2 :
    Get the corresponding endpoints and the relevant keys for the two service instances created in Step 1 and enter them in the .env file 

Step 3 :
    In file news_collector.py adjust the timings for the nightly (scraping, translation, summarization, sentiment analysis and storage) job and that of the morning job (the morning job is responsible for reading out the summary of the news in the morning while you make your coffee)
    <img width="490" alt="image" src="https://github.com/mtc9517/news-translator-summarizer-player/assets/10408445/e98f0b40-6ff9-4bdf-bceb-9153d3e05e57">

Step 4 :
    % python news_collector.py

[ The following step (Step 5) starts up a web server and one can browse to the website for viewing the summary (as well the full version) of the news for that day ]

Step 5 :
    % streamlit run news_displayer.py

<img width="1227" alt="image" src="https://github.com/mtc9517/news-translator-summarizer-player/assets/10408445/68ee6e86-b617-4775-ab61-ff0a71e8f83a">
