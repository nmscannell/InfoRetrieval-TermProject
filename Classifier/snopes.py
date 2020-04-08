import requests
from bs4 import BeautifulSoup
import csv
'''
URL = 'https://www.politifact.com/factchecks/2020/mar/31/facebook-posts/wisconsin-coronavirus-cases-peak-april-26-may-22/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
section = soup.find(class_='m-textblock')
section = section.find_all('p')

print(section)
#results = section.get_text()
#print(results)'''

URL = "https://www.snopes.com/collections/new-coronavirus-collection/"
snopes = []
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
section = soup.find(class_='card-body')
links = [a['href'] for a in section.find_all('a', href=True) if a['href'].count('collection') != 0]

for url in links:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    section = soup.find(class_='collected-list col-12')
    for a in section.find_all('a', href=True):
        text = a.find(class_='media-body').get_text().strip()
        if text != 'False' and text != 'True':
            continue
        if a['href'] not in snopes:
            snopes.append(a['href'])

URL = "https://www.snopes.com/fact-check/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

while len(snopes) < 1000:
    media = soup.find(class_='theme-content').find(class_='base-main').find(class_='media-list')
    for a in media.find_all('a', href=True):
        if a['href'] not in snopes:
            snopes.append(a['href'])
    url = soup.find(class_='pagination btn-group').find(class_='btn-next btn')
    if len(url) == 0:
        break
    url = url['href']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

print('done getting snopes links')

t_links = []
f_links = []

for url in snopes:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    rating = soup.find(class_='rating-wrapper card').find('h5').get_text().strip()
    if rating != 'True' and rating != 'False':
        continue
    content = soup.find(class_='content-wrapper card').find(class_='content')
    p = content.find_all('p')
    i = 0
    while i < 2:
        section = p[i].find_all('a', href=True)
        i += 1
        if len(section) == 0:
            continue
        for a in section:
            if 'snopes' in a['href'] or 'twitter' in a['href'] or 'youtu' in a['href'] or 'images' in a['href']:
                continue
            if 'bbc' in a['href'] or '.gov' in a['href'] or 'cnbc' in a['href'] or 'reuters' in \
                a['href'] or 'politico' in a['href'] or 'washingtontimes' in a['href'] or 'newyorktimes' \
                    in a['href'] or 'nbc' in a['href']:
                t_links.append(a['href'])
            else:
                if rating == 'True':
                    t_links.append(a['href'])
                else:
                    f_links.append(a['href'])
    print('true: ' + str(len(t_links)))
    print('false: ' + str(len(f_links)))
    if len(t_links) + len(f_links) > 500:
        break


# store links in csv
with open('sources.csv', 'w') as csvf:
    writer = csv.writer(csvf)
    for i in t_links:
        writer.writerow([i] + [str(1)])
    for i in f_links:
        writer.writerow([i] + [str(0)])
