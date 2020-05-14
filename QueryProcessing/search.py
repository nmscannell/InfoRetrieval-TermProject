from googleapiclient.discovery import build


my_api_key = ""
my_cse_id = ''


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    results = []
    results.append(service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()['items'])
    results.append(service.cse().list(q=search_term, cx=cse_id, start=11, **kwargs).execute()['items'])
    return results


def perform_search(query):
    return google_search(query, my_api_key, my_cse_id)

