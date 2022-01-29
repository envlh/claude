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
    query = '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategoryLabel (GROUP_CONCAT(?genderLabel_ ; separator=",") AS ?genderLabel) {
  # VALUES ?lexeme { wd:L641558 } .
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory .
  FILTER (?lexicalCategory != wd:Q147276) . # nom propre
  ?lexicalCategory rdfs:label ?lexicalCategoryLabel .
  FILTER(LANG(?lexicalCategoryLabel) = "fr") .
  OPTIONAL {
    ?lexeme wdt:P5185 ?gender .
    ?gender rdfs:label ?genderLabel_ .
    FILTER(LANG(?genderLabel_) = "fr")
  }
}
GROUP BY ?lexeme ?lemma ?lexicalCategoryLabel
LIMIT 100000
'''
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    return json.loads(fetch_url(url).content)['results']['bindings']


def crawl_url(cnx, cursor, url):
    r = fetch_url(url)
    status_code = r.status_code
    headers = json.dumps(dict(r.headers), ensure_ascii=False)
    content = r.text
    data = (url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_code, headers, content)
    cursor.execute('INSERT INTO `crawl`(`url`, `date`, `status_code`, `headers`, `content`) VALUES(%s, %s, %s, %s, %s)', data)
    cnx.commit()
    time.sleep(10)
    return {'status_code': status_code, 'headers': headers, 'content': content}


def get_or_fetch_lemma(cnx, cursor, normalized_lemma):
    url = 'https://dictionnaire.lerobert.com/definition/{}'.format(normalized_lemma)
    cursor.execute('SELECT `status_code`, `headers`, `content` FROM `crawl` WHERE `url` = %s ORDER BY `date` DESC LIMIT 1', (url,))
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        return {'status_code': row[0], 'headers': row[1], 'content': row[2]}
    return crawl_url(cnx, cursor, url)


def normalize_lemma(lemma):
    return re.sub(r'[^a-z]', '-', unidecode.unidecode(lemma).lower())


def is_matching(content, lemma, lexical_category, gender):
    valids = set()
    for h3 in re.findall(re.compile('<h3>(.*?)</h3>', re.DOTALL), content):
        # multiple sounds
        h3_cleaned = re.sub(re.compile('<span class="d_sound_sep"> \\| </span>', re.DOTALL), '', h3)
        # sound
        h3_cleaned = re.sub(re.compile('<span class="d_sound_cont"><sound.*?sound></span>', re.DOTALL), '', h3_cleaned)
        # nom déposé
        h3_cleaned = re.sub(re.compile('<span class="d_etm">\\(nom déposé\\)</span>', re.DOTALL), '', h3_cleaned)
        match = re.search(re.compile('^(.*?)<span class="d_cat">(.*)</span>', re.DOTALL), h3_cleaned)
        if match is not None:
            lem_matches = re.split('(?:, )|(?: <span class="d_mta">ou</span> )', match.group(1).strip())
            lexcat_matches = re.split('(?:, )|(?: <span class="d_x">et</span> )', match.group(2).strip())
            for lem_match in lem_matches:
                for lexcat_match in lexcat_matches:
                    valids.add((lem_match, lexcat_match))
    for (lem_match, lexcat_match) in valids:
        if lem_match == lemma:
            if lexical_category != 'nom' and lexcat_match == lexical_category:
                return True
            if lexical_category == 'numéral' and lexcat_match == 'adjectif numéral invariable':
                return True
            if lexical_category == 'nom' and '{} {}'.format(lexical_category, gender) == lexcat_match:
                return True
            if lexical_category == 'nom' and lexcat_match == 'nom' and (gender == 'féminin,masculin' or gender == 'masculin,féminin'):
                return True
            if lexical_category == 'verbe' and lexcat_match in ('verbe intransitif', 'verbe pronominal', 'verbe transitif', 'verbe transitif indirect'):
                return True
    # print('{} : {}, {} - {}'.format(lemma, lexical_category, gender, valids))
    return False


def main():
    db_config = load_json_file('conf/general.json')['database']
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    lexemes = fetch_lexemes_to_crawl()
    ko_not_200 = 0
    ko_not_matching = 0
    http_codes = {}
    for lexeme in lexemes:
        lid = lexeme['lexeme']['value'][31:]
        lemma = lexeme['lemma']['value']
        lexical_category = lexeme['lexicalCategoryLabel']['value']
        gender = None
        if 'genderLabel' in lexeme:
            gender = lexeme['genderLabel']['value']
        normalized_lemma = normalize_lemma(lemma)
        r = get_or_fetch_lemma(cnx, cursor, normalized_lemma)
        if r['status_code'] != 200:
            ko_not_200 += 1
            if r['status_code'] not in http_codes:
                http_codes[r['status_code']] = 0
            http_codes[r['status_code']] += 1
        elif not is_matching(r['content'], lemma, lexical_category, gender):
            ko_not_matching += 1
        # else:
            # print('{} : {}, {}'.format(lemma, lexical_category, gender))
    ko_total = ko_not_200 + ko_not_matching
    print('lexemes: {}, OK: {}, KO: {}, KO (not 200): {}, KO (not matching): {}, HTTP codes: {}'.format(len(lexemes), len(lexemes) - ko_total, ko_total, ko_not_200, ko_not_matching, http_codes))


if __name__ == '__main__':
    main()
