import pywikibot
import utils

from db import DB
from lerobert import LeRobert
from littre import Littre
from tlfi import Tlfi


# https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim&uselang=en
def add_value(site, db, entity_id, property_id, value, edit_summary):
    request = {
        'action': 'wbcreateclaim',
        'entity': entity_id,
        'snaktype': 'value',
        'property': property_id,
        'value': '"{}"'.format(value),
        'summary': edit_summary,
        'token': site.tokens['edit'],
        'bot': '1',
    }
    db.save_history(entity_id, property_id, value)
    site._simple_request(**request).submit()


def get_site():
    site = pywikibot.Site('wikidata', 'wikidata')
    site.login()
    return site


def main():
    site = get_site()
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dicos = [Tlfi(db)]
    for dico in dicos:
        print('Processing {}...'.format(dico.get_property_id()))
        lexemes = dico.fetch_lexemes_to_crawl()
        success_count = 0
        errors = dict()
        ref = dict()
        for lexeme in lexemes:
            lexeme_id = lexeme['lexeme']['value'][31:]
            if not db.exists_history(lexeme_id, dico.get_property_id()):
                success, inferred_id = dico.process(lexeme)
                if success:
                    add_value(site, db, lexeme_id, dico.get_property_id(), inferred_id, dico.get_edit_summary())
                    success_count += 1
                else:
                    errors[lexeme_id] = inferred_id
                    ref[lexeme_id] = lexeme
            else:
                print('Lexeme {} previously imported, not trying again.'.format(lexeme_id))
        print('lexemes: {}, success: {}'.format(len(lexemes), success_count))


if __name__ == '__main__':
    main()
