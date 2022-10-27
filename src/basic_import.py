import bot
import json
import re
import string
import utils

from db import DB
from larousse import Larousse
from lerobert import LeRobert
from littre import Littre
from tlfi import Tlfi
from tlfi_index import TlfiIndex


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    index = TlfiIndex(db)
    dicos = [Larousse(db), LeRobert(db), Littre(db), Tlfi(db)]
    existing = set()
    lemmas = utils.sparql_query('SELECT DISTINCT (STR(?lemma) AS ?str) { [] dct:language wd:Q150 ; wikibase:lexicalCategory wd:Q24905 ; wikibase:lemma ?lemma }')
    for lemma in lemmas:
        existing.add(lemma['str']['value'])
    todo = {}
    for letter in list(string.ascii_uppercase):
        page = 'portailindex/LEXI/TLFI/{}'.format(letter)
        while page is not None:
            r_index = index.get_or_fetch_by_id(page)
            # forms
            matches = re.findall(re.compile('<td><a href="/definition/(?:.*?)" title="Définition de (?:.*?)">(.*?)</a></td>', re.DOTALL), r_index['content'])
            if matches is not None:
                for match in matches:
                    if match[-2:] in ('er', 'ir') and match[:3] != 'se ' and 'î' not in match and match not in existing:
                        kept = {}
                        for dico in dicos:
                            inferred_id = dico.infer_id(match)
                            r = dico.get_or_fetch_by_id(inferred_id)
                            if r['status_code'] in (301, 302):
                                inferred_id = dico.get_id_from_redirect(r)
                                if inferred_id is not None:
                                    r = dico.get_or_fetch_by_id(inferred_id)
                            if r['status_code'] == 200:
                                keep = set()
                                candidates = dico.parse_content(r['content'], inferred_id)
                                for candidate in candidates:
                                    if candidate.lemma == match and candidate.lexical_category == dico.VERB:
                                        keep.add(candidate)
                                if len(keep) == 1:
                                    kept[dico.get_property_id()] = keep.pop().parsed_id
                        if len(kept.keys()) >= 3:
                            # print(match)
                            todo[match] = kept
            # next page
            match = re.search(re.compile('<a href="/(portailindex/[A-Z0-9/]+)"><img src="/images/portail/right.gif" title="Page suivante" border="0" width="32" height="32" alt="" /></a>', re.DOTALL), r_index['content'])
            if match is not None:
                page = match.group(1)
            else:
                page = None
    print(len(todo))
    # utils.file_put_contents('data/test.json', json.dumps(dict(todo), ensure_ascii=False))
    site = bot.get_site()
    # trick to randomize order
    lemmas = set(todo.keys())
    for lemma in lemmas:
        lexeme = {'type': 'lexeme', 'language': 'Q150', 'lemmas': {'fr': {'language': 'fr', 'value': lemma}}, 'lexicalCategory': 'Q24905', 'forms': [{'representations': {'fr': {'language': 'fr', 'value': lemma}}, 'grammaticalFeatures': ['Q179230'], 'add': ''}], 'claims': {}}
        for pid in todo[lemma]:
            lexeme['claims'][pid] = [{'mainsnak': {'snaktype': 'value', 'property': pid, 'datavalue': {'value': todo[lemma][pid], 'type': 'string'}, 'datatype': 'external-id'}, 'type': 'statement', 'rank': 'normal'}]
        if lemma[-2:] == 'er':
            lexeme['claims']['P5186'] = [{'mainsnak': {'snaktype': 'value', 'property': 'P5186', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 2993354,'id': 'Q2993354'}, 'type': 'wikibase-entityid'}, 'datatype': 'wikibase-item'}, 'type': 'statement', 'rank': 'normal'}]
        elif lemma[-2:] != 'ir' or lemma[-3:] == 'oir':
            lexeme['claims']['P5186'] = [{'mainsnak': {'snaktype': 'value', 'property': 'P5186', 'datavalue': {'value': {'entity-type': 'item', 'numeric-id': 2993358, 'id': 'Q2993358'}, 'type': 'wikibase-entityid'}, 'datatype': 'wikibase-item'}, 'type': 'statement', 'rank': 'normal'}]
        generated_json = json.dumps(dict(lexeme), ensure_ascii=False)
        # print(generated_json)
        bot.create_lexeme(site, generated_json, '')


if __name__ == '__main__':
    main()
