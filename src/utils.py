import json
import requests
import urllib.parse


def file_get_contents(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        s = f.read()
    return s


def load_set(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        s = f.readlines()
    return set(s)


def file_put_contents(filename, content):
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(content)


def load_json_file(filename):
    return json.loads(file_get_contents(filename))


def fetch_url(url):
    return requests.get(url, headers={'User-Agent': 'claude/0.1'}, allow_redirects=False)


def sparql_query(query):
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    return json.loads(fetch_url(url).content)['results']['bindings']
