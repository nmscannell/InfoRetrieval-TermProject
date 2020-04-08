from newsapi import NewsApiClient
import csv
# source, url, title, content, label
# Init
newsapi = NewsApiClient(api_key='92a066c49fa74acf9abfe52b04d5c7e4')
reliable = ''
with open('../reliable.txt', 'r') as f:
    for line in f:
        reliable += line
        reliable += ','
unreliable = ''
with open('../unreliable.txt', 'r') as f:
    for line in f:
        unreliable += line
        unreliable += ','

'''
# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q='coronavirus',sources='the-huffington-post')['articles']

# /v2/everything
all_articles = newsapi.get_everything(q='bitcoin',
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

'''
with open('../medical_topics.txt', 'r') as f:
    with open('data.csv', 'a') as csvf:
        writer = csv.writer(csvf)
        for line in f:
            articles = newsapi.get_everything(q=line, sources=reliable[:len(reliable)-1])['articles']
            for a in articles:
                row = []
                row.append(a['source']['name'])
                row.append(a['url'])
                row.append(a['title'])
                row.append(a['content'])
                row.append(str(1))
                writer.writerow(row)
            articles = newsapi.get_everything(q=line, sources=unreliable[:len(unreliable) - 1])['articles']
            for a in articles:
                row = []
                row.append(a['source']['name'])
                row.append(a['url'])
                row.append(a['title'])
                row.append(a['content'])
                row.append(str(0))
                writer.writerow(row)
'''
with open('data.csv', 'a') as csvf:
    writer = csv.writer(csvf)
    articles = newsapi.get_everything(sources=reliable[:len(reliable)-1])['articles']
    for a in articles:
        row = []
        row.append(a['source']['name'])
        row.append(a['url'])
        row.append(a['title'])
        row.append(a['content'])
        row.append(str(1))
        writer.writerow(row)
    articles = newsapi.get_everything(sources=unreliable[:len(unreliable) - 1])['articles']
    for a in articles:
        row = []
        row.append(a['source']['name'])
        row.append(a['url'])
        row.append(a['title'])
        row.append(a['content'])
        row.append(str(0))
        writer.writerow(row)

# to get source name: a['source']['name']
# to get url: a['url']
# to get title: a['title']
# to get content: a['content']