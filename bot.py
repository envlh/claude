# import pywikibot
import utils

from db import DB
from lerobert import LeRobert


# https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim&uselang=en
def add_value(site, entity_id, property_id, value):
    request = {
        'action': 'wbcreateclaim',
        'entity': entity_id,
        'snaktype': 'value',
        'property': property_id,
        'value': value,
        'summary': 'test',
        'token': site.tokens['edit'],
        'bot': '1',
    }
    site._simple_request(**request).submit()


def get_site():
    site = pywikibot.Site('test', 'wikidata')
    site.login()
    return site


def main():
    # site = get_site()
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = LeRobert(db)
    lexemes = dico.fetch_lexemes_to_crawl()
    success_count = 0
    for lexeme in lexemes:
        success, lexeme_id, inferred_id = dico.process(lexeme)
        if success:
            # add_value(site, lexeme_id, dico.get_property_id(), '"{}"'.format(inferred_id))
            success_count += 1
        # print('{} {} {}'.format(success, lexeme_id, inferred_id))
    print('lexemes: {}, success: {}'.format(len(lexemes), success_count))


if __name__ == '__main__':
    main()
