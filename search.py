from googleapiclient.discovery import build


my_api_key = "AIzaSyABgnJx_9wc1XUkcxxu37kkFjuSkdRAoyg"
my_cse_id = "014077842480068895608:izuv4zk2qgl"


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res


def perform_search(query):
    return google_search(query, my_api_key, my_cse_id)['items']
