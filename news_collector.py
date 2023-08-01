import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import re
import os
import sys
import json
import schedule
import time
import azure.cognitiveservices.speech as speech_sdk


from dotenv import load_dotenv
from datetime import datetime

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.textanalytics import ExtractSummaryAction




from pathlib import Path
import shutil



from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

global translator_endpoint
global cog_key
global cog_region
global language_resource_key
global language_resource_endpoint
global speech_config


# Functions defination starts
def GetLanguage(text):
    # Default language is English
    language = 'en'

    # Use the Translator detect function
    # Use the Translator detect function
    path = '/detect'
    url = translator_endpoint + path

    # Build the request
    params = {
        'api-version': '3.0'
    }

    headers = {
    'Ocp-Apim-Subscription-Key': cog_key,
    'Ocp-Apim-Subscription-Region': cog_region,
    'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()

    # Parse JSON array and get language
    language = response[0]["language"]

    # Return the language
    return language

def Translate(text, source_language):
    translation = ''

    # Use the Translator translate function
    path = '/translate'
    url = translator_endpoint + path

    # Build the request
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': ['en']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': cog_key,
        'Ocp-Apim-Subscription-Region': cog_region,
        'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()

    # Parse JSON array and get translation
    translation = response[0]["translations"][0]["text"]

    # Return the translation
    return translation

# Authenticate the client using your key and endpoint
def authenticate_client():
    key = language_resource_key
    endpoint = language_resource_endpoint

    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=ta_credential)
    return text_analytics_client

def extractive_summary_of_text(client, text):

    poller = client.begin_analyze_actions(
        text,
        actions=[
            ExtractSummaryAction(max_sentence_count=4, order_by="Rank")
        ],
    )

    document_results = poller.result()
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            summary = format(" ".join([sentence.text for sentence in extract_summary_result.sentences]))
            print("\n" + "The extracted summary is as follows: " + summary + "\n")
    return summary

def SynthesizeToSpeechUsingREST(text):
    response_text = text


    # Configure speech synthesis
    #speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural' # change this
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # Synthesize spoken output
    responseSsml = " \
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
            <voice name='en-GB-LibbyNeural'> \
                {} \
                <break strength='weak'/> \
                That was a scraped and summarized news article from a news site of Ukraine, Time to move on to the next piece of summarised news! \
            </voice> \
        </speak>".format(response_text)
    speak = speech_synthesizer.speak_ssml_async(responseSsml).get()

    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

def SynthesizeToSpeechUsingSDK(text):
    response_text = text


    # Configure speech synthesis
    #speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural' # change this
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    speak = speech_synthesizer.speak_text_async(response_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

# Function defination ends

# Get Configuration Settings
#os.environ.pop('COG_SERVICE_REGION')

load_dotenv()
cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
cog_key = os.getenv('COG_SERVICE_KEY')
language_resource_key = os.getenv('LANGUAGE_RESOURCE_KEY')
cog_region = os.getenv('COG_SERVICE_REGION')
translator_endpoint = 'https://api.cognitive.microsofttranslator.com'
#language_resource_endpoint = 'https://language-service-resource-prk.cognitiveservices.azure.com'
language_resource_endpoint = os.getenv('LANGUAGE_RESOURCE_ENDPOINT')

# Create client using endpoint and key
credential = AzureKeyCredential(cog_key)
cog_client = TextAnalyticsClient(endpoint=cog_endpoint, credential=credential)
lang_client = authenticate_client()
# Configure speech service
speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)

website_to_scrape = "https://strana.news/"
main_link = "https://strana.news/"
dir_to_download = 'downloads_all'



def nightly_job():
    #The requests module allows you to send HTTP requests using Python.
    #It returns a Response Object with all the response data (content, encoding, status, etc).
    response_http = requests.get(website_to_scrape)
    url_of_child_pages_list = []
    soup3 = BeautifulSoup(response_http.content, 'html.parser')
    for link in soup3.find_all('a'):
        detail_link = link.get('href')
        if detail_link.startswith('/news/'):
            url_of_child_pages_list.append(main_link + detail_link)

    ix = 0

    translated_article = ""

    url_of_child_pages_list = list(set(url_of_child_pages_list))

    dirpath = Path('.') / dir_to_download
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)

    if not os.path.exists(dir_to_download):
       os.makedirs(dir_to_download)


    for url in url_of_child_pages_list:

        # initialize the translated_article string at the beginning of every iteration
        translated_article = ""

        req = requests.get(url)

        soup = bs(req.text, 'html.parser')
        s = soup.find('div', id= "article-body")

        # Getting the title tag
        print(soup.title)

        lines = s.find_all('p')
        for line in lines:

            text = line.text
            # Detect the language
            language = GetLanguage(text)

            translation = text
            # Translate if not already English (line by line)
            if language != 'en':
                translation = Translate(text, language)
            translated_article = translated_article + translation

        article_to_summarize = [translated_article]
        extracted_short_summary = extractive_summary_of_text(lang_client, article_to_summarize)

        # Get sentiment
        sentimentAnalysis = cog_client.analyze_sentiment(documents=[extracted_short_summary])[0]

        f = open(dir_to_download + "/news_full_article_" + str(ix) + sentimentAnalysis.sentiment + ".txt", "w")
        f.write(translated_article)
        f.close()
        f = open(dir_to_download + "/news_summary_article_" + str(ix) + sentimentAnalysis.sentiment + ".txt", "w")
        f.write(extracted_short_summary)
        f.close()

        ix = ix + 1

def morning_job():
	# Get the list of all files and directories
	dir_list = os.listdir(dir_to_download)
	dir_summary_list = []
	for x in dir_list:
		if 'summary' in x:
			dir_summary_list.append(x)

	for complete_text_file_name in dir_summary_list:
		with open(dir_to_download + '/' + complete_text_file_name) as f:
			contents = f.read()
			f.close()
			SynthesizeToSpeechUsingREST(contents)

			if "negative" in complete_text_file_name:
				sentiment_statement = "Unfortunately as per my analysis this piece of news carries a negative sentiment"
				SynthesizeToSpeechUsingSDK(sentiment_statement)
			if "positive" in complete_text_file_name:
				sentiment_statement = "Woo Hoo as per my analysis this piece of news carries a positive sentiment"
				SynthesizeToSpeechUsingSDK(sentiment_statement)
			if "neutral" in complete_text_file_name:
				sentiment_statement = "Hmmm as per my analysis this piece of news carries a neutral sentiment"
				SynthesizeToSpeechUsingSDK(sentiment_statement)

# Run job every day at specific HH:MM:SS
schedule.every().day.at("19:00:42").do(nightly_job)
schedule.every().day.at("20:00:42").do(morning_job)

while True:
    schedule.run_pending()
    time.sleep(1)
