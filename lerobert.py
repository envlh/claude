import json
import os.path
import re
import requests
import time
import unidecode
import urllib.parse


def fetch_url(url):
    return requests.get(url, headers={'User-Agent': 'wd-lex-dict-sync/0.1'}, allow_redirects=False)


def fetch_lexemes_to_crawl():
    query = 'SELECT DISTINCT ?lexeme ?lemma { ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma } LIMIT 100000'
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    return json.loads(fetch_url(url).content)['results']['bindings']


def get_file_path(normalized_lemma, ext='json'):
    return 'data/lerobert/{}.{}'.format(normalized_lemma, ext)


def is_cached(normalized_lemma):
    return os.path.isfile(get_file_path(normalized_lemma))


def crawl_lemma(normalized_lemma):
    url = 'https://dictionnaire.lerobert.com/definition/{}'.format(normalized_lemma)
    r = fetch_url(url)
    with open(get_file_path(normalized_lemma, 'http'), 'w', encoding='utf-8') as content_file:
        content_file.write(str(r.status_code))
    with open(get_file_path(normalized_lemma, 'json'), 'w', encoding='utf-8') as headers_file:
        json.dump(dict(r.headers), headers_file, ensure_ascii=False)
    with open(get_file_path(normalized_lemma, 'html'), 'w', encoding='utf-8') as content_file:
        content_file.write(r.text)
    return r.status_code


def normalize_lemma(lemma):
    return re.sub(r'[^a-z]', '-', unidecode.unidecode(lemma).lower())


def main():
    lexemes = fetch_lexemes_to_crawl()
    for lexeme in lexemes:
        lid = lexeme['lexeme']['value'][31:]
        lemma = lexeme['lemma']['value']
        normalized_lemma = normalize_lemma(lemma)
        if not is_cached(normalized_lemma):
            status_code = crawl_lemma(normalized_lemma)
            print('{} {} {} {}'.format(lid, lemma, normalized_lemma, status_code))
            time.sleep(10)


if __name__ == '__main__':
    main()
