import json
import requests


def file_get_contents(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        s = f.read()
    return s


def load_json_file(filename):
    return json.loads(file_get_contents(filename))


def fetch_url(url):
    return requests.get(url, headers={'User-Agent': 'wd-lex-dict-sync/0.1'}, allow_redirects=False)
