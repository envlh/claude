import json
import re
import urllib.parse
import utils

from db import DB
from tlfi import Tlfi


def log_error(lexeme_id, tlfi_id, status_code):
    print('|-\n| [[Lexeme:{}|{}]]\n| {}\n| [https://www.cnrtl.fr/definition/{} link]\n| {}'.format(lexeme_id, lexeme_id, tlfi_id, tlfi_id, status_code))


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = Tlfi(db)
    query = 'SELECT DISTINCT ?lexeme ?id { ?lexeme wdt:P7722 ?id } ORDER BY ?id'
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    lexemes = json.loads(utils.fetch_url(url).content)['results']['bindings']
    print('{| class="wikitable sortable"\n! Lexeme\n! TLFi ID\n! Link\n! Status code')
    for lexeme in lexemes:
        lexeme_id = lexeme['lexeme']['value'][31:]
        tlfi_id = lexeme['id']['value']
        r = dico.get_or_fetch_by_id(tlfi_id)
        if r['status_code'] != 200:
            log_error(lexeme_id, tlfi_id, r['status_code'])
        else:
            match = re.search(re.compile('<span>.*?<sup>1</sup></span>', re.DOTALL), r['content'])
            if match is not None:
                log_error(lexeme_id, tlfi_id, r['status_code'])
    print('|}')


if __name__ == '__main__':
    main()
