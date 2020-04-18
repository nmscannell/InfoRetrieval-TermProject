import sys
import os
import django

sys.path.append('/home/scannell/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'TRTerm.settings'
django.setup()

from Index.Indexer import Indexer


indexer = Indexer()

for i in range(1, 27):
    indexer.process_file('files/' + str(i)+'.txt')

#with open('urls.txt') as f:
#    for line in f:
#        print(line)
#        indexer.scrape_web(line.strip('\n'))

print(indexer.index)
