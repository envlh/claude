from datetime import datetime
import json
import mysql.connector
import re
import requests
import time
import unidecode
import urllib.parse


def file_get_contents(filename):
    with open(filename, 'r', encoding='UTF-8') as f:
        s = f.read()
    return s


def load_json_file(filename):
    return json.loads(file_get_contents(filename))


def fetch_url(url):
    return requests.get(url, headers={'User-Agent': 'wd-lex-dict-sync/0.1'}, allow_redirects=False)


def fetch_lexemes_to_crawl():
    query = 'SELECT DISTINCT ?lexeme ?lemma { ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma } LIMIT 100000'
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    return json.loads(fetch_url(url).content)['results']['bindings']


def is_cached_url(cursor, url):
    cursor.execute('SELECT COUNT(*) AS `count` FROM `crawl` WHERE `url` = %s', (url,))
    row = cursor.fetchone()
    if row[0] >= 1:
        return True
    else:
        return False


def crawl_url(cursor, url):
    r = fetch_url(url)
    data = (url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(r.status_code), json.dumps(dict(r.headers), ensure_ascii=False), r.text)
    cursor.execute('INSERT INTO `crawl`(`url`, `date`, `status_code`, `headers`, `content`) VALUES(%s, %s, %s, %s, %s)', data)
    return r.status_code


def normalize_lemma(lemma):
    return re.sub(r'[^a-z]', '-', unidecode.unidecode(lemma).lower())


def main():
    db_config = load_json_file('conf/general.json')['database']
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    lexemes = fetch_lexemes_to_crawl()
    for lexeme in lexemes:
        lid = lexeme['lexeme']['value'][31:]
        lemma = lexeme['lemma']['value']
        normalized_lemma = normalize_lemma(lemma)
        url = 'https://dictionnaire.lerobert.com/definition/{}'.format(normalized_lemma)
        if not is_cached_url(cursor, url):
            status_code = crawl_url(cursor, url)
            cnx.commit()
            print('{} {} {} {}'.format(lid, lemma, normalized_lemma, status_code))
            time.sleep(10)


if __name__ == '__main__':
    main()
