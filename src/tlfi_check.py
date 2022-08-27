import json
import re
import urllib.parse
import utils

from db import DB
from tlfi import Tlfi


def log_error(lexeme_id, tlfi_id, error):
    print('|-\n| [[Lexeme:{}|{}]]\n| {}\n| [https://www.cnrtl.fr/definition/{} TLFi]\n| {}'.format(lexeme_id, lexeme_id, tlfi_id, tlfi_id, error))


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = Tlfi(db)
    query = 'SELECT DISTINCT ?lexeme ?id { ?lexeme wdt:P7722 ?id } ORDER BY ?id'
    url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
    lexemes = json.loads(utils.fetch_url(url).content)['results']['bindings']
    print('{| class="wikitable sortable"\n! Lexème\n! P7722\n! Lien\n! Erreur')
    for lexeme in lexemes:
        lexeme_id = lexeme['lexeme']['value'][31:]
        tlfi_id = lexeme['id']['value']
        tlfi_id_base = re.sub('/[0-9]+$', '', tlfi_id)
        tlfi_id_tab = re.sub('^.*?/', '', tlfi_id)
        if tlfi_id_tab == tlfi_id:
            tlfi_id_tab = 0
        r = dico.get_or_fetch_by_id(tlfi_id_base)
        # erreur de crawling
        if r['status_code'] != 200:
            log_error(lexeme_id, tlfi_id, 'Le crawling a retourné l\'erreur HTTP <code>{}</code>.'.format(r['status_code']))
            continue
        # forme inexistante
        match = re.search(re.compile('Cette forme est introuvable'), r['content'])
        if match is not None:
            log_error(lexeme_id, tlfi_id, 'L\'identifiant n\'existe pas.')
        match = re.search(re.compile('Terme introuvable'), r['content'])
        if match is not None:
            log_error(lexeme_id, tlfi_id, 'L\'identifiant n\'existe pas.')
        # forme composée id/n avec la seconde partie manquante
        match = re.search(re.compile('return sendRequest\\(5,\'/definition/.*?//1\'\\);'), r['content'])
        if match is not None and '/' not in tlfi_id:
            log_error(lexeme_id, tlfi_id, 'L\'identifiant devrait préciser le numéro de l\'onglet sous la forme <code>{}/numéro</code>.'.format(tlfi_id.lower()))
        else:
            # l'identifiant fonctionne mais n'est pas celui proposé par le TLFi
            match = re.search(re.compile('<a href="#" onclick="return sendRequest\\(5,\'/definition/.*?//{}\'\\);"><span>(.*?)(?:<sup>[0-9]+</sup>)?</span>.*?</a>'.format(tlfi_id_tab)), r['content'])
            if match is None:
                log_error(lexeme_id, tlfi_id, 'Impossible de trouver l\'onglet actif.')
            elif '(' not in match[1]:
                tlfi_lemmas = set()
                matched_lemmas = re.sub(r'<sup>[0-9]+</sup>', '', match[1]).lower().split(', ')
                for lemma in matched_lemmas:
                    if lemma[:1] != '-':
                        tlfi_lemmas.add(lemma)
                    else:
                        first_char = lemma[1:2]
                        position = matched_lemmas[0].rfind(first_char)
                        tlfi_lemmas.add(matched_lemmas[0][:position] + lemma[1:])
                if tlfi_id_base not in tlfi_lemmas:
                    log_error(lexeme_id, tlfi_id, 'La base de l\'identifiant ne respecte pas l\'orthographe du mot vedette (valeurs correctes : <code>{}</code>).'.format('</code>, <code>'.join(tlfi_lemmas)))
    print('|}')


if __name__ == '__main__':
    main()
