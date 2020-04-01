from googleapiclient.discovery import build
import sys
import urllib.request
import urllib.parse
import re
from urllib.request import urlopen as ureqs
from bs4 import BeautifulSoup as soup
from newsapi import NewsApiClient


my_api_key = "AIzaSyABgnJx_9wc1XUkcxxu37kkFjuSkdRAoyg"
my_cse_id = "014077842480068895608:izuv4zk2qgl"


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res


def youtube_search(query):
    query_string = urllib.parse.urlencode({"search_query" : query})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    pass


# Init
newsapi = NewsApiClient(api_key='92a066c49fa74acf9abfe52b04d5c7e4')

# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q='coronavirus')['articles']

# /v2/everything
'''all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2017-12-01',
                                      to='2017-12-12',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)

# /v2/sources
sources = newsapi.get_sources()
'''

results = google_search("natasha scannell", my_api_key, my_cse_id)['items']
for i in results:
    print(i['title'])


for i in top_headlines:
    print(i['source'])
#print(top_headlines)
