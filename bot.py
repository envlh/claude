import pywikibot
import utils

from db import DB
from lerobert import LeRobert
from littre import Littre


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
    dicos = [LeRobert(db), Littre(db)]
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
        errors = dict(sorted(errors.items(), key=lambda item: item[1]))
        errors_string = '{| class="wikitable sortable"\n! Lexeme\n! Lemma\n! Lexical category\n! Grammatical gender\n! Inferred ID\n'
        for lexeme_id in errors:
            errors_string += '|-\n'
            errors_string += '| [[Lexeme:' + lexeme_id + '|' + lexeme_id + ']]\n'
            errors_string += '| ' + ref[lexeme_id]['lemma']['value'] + '\n'
            errors_string += '| ' + ref[lexeme_id]['lexicalCategoryLabel']['value'] + '\n'
            errors_string += '| '
            if 'genderLabel' in ref[lexeme_id]:
                errors_string += ref[lexeme_id]['genderLabel']['value']
            errors_string += '\n'
            errors_string += '| '
            if errors[lexeme_id] != '':
                errors_string += '[' + dico.get_url().format(errors[lexeme_id]).replace(' ', '%20') + ' ' + errors[lexeme_id] + ']'
            errors_string += '\n'
        errors_string += '|}'
        report_page = pywikibot.Page(site, 'User:EnvlhBot/Reports/{}'.format(dico.get_property_id()))
        report_page.text = errors_string
        # report_page.save('Report update for {}'.format(dico.get_edit_summary()))
        utils.file_put_contents('data/report_errors.txt', errors_string)
        print('lexemes: {}, success: {}'.format(len(lexemes), success_count))


if __name__ == '__main__':
    main()
