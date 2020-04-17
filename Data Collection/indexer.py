import nltk
from nltk.corpus import stopwords
from medsearch.models import Document
import pickle

'''
Indexer parses and stores data in the database.
Data pulled from xlsx file or from web scraper.
All terms are lowercased, punctuation and stop words are removed.

Inverted index contains search terms with postings lists that contains term frequency for each docID
Inverted index is stored in a dict that is saved and loaded via pickle.
'''


def process_file(file):
    pass


def scrape_web(url):
    pass


def store_doc(id, url, type, title, summary, date):
    if Document.objects.filter(url=url).exists():
        return False

    D = Document()
    D.docID = id
    D.url = url
    D.type = type
    D.title = title
    D.summary = summary
    D.date = date
    D.save()
    return True


def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
