import csv
import re
import utils

from db import DB
from academie_index import AcademieIndex


def main():
    configuration = utils.load_json_file('conf/general.json')
    db = DB(configuration['database'])
    dico = AcademieIndex(db)
    todo = set()
    todo.add('A0001')
    # todo.add('B0876')
    done = set()
    with open('data/academie_candidates.csv', 'w', newline='', encoding='UTF-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        while len(todo) >= 1:
            todo_id = todo.pop()
            done.add(todo_id)
            r = dico.get_or_fetch_by_id('A9{}'.format(todo_id))
            if r['status_code'] == 200:
                content = re.sub('&#039;', '\'', re.sub('<span class="edition">.*?</span>', '', r['content']))
                # other ids
                found_ids = re.findall('/article/A9([A-Z][0-9]{4}[A-Z0-9-]*)"', content)
                for found_id in found_ids:
                    if found_id not in done:
                        todo.add(found_id)
                # lemmas
                matched_lemmas = set()
                lemmas_string = re.findall('<h1>(.*?)</h1>', content)[0]
                parsed_lemmas = lemmas_string.split(', ')
                for lemma in parsed_lemmas:
                    if lemma[:1] != '-':
                        matched_lemmas.add(lemma)
                    else:
                        first_char = lemma[1:2]
                        position = parsed_lemmas[0].rfind(first_char)
                        matched_lemmas.add(parsed_lemmas[0][:position] + lemma[1:])
                # lexical categories
                matched_lexical_categories = set()
                parsed_lexical_categories = re.findall('<li class="motActif">[\n\r\t ]*<a href="../article/[A-Z0-9-]+">{}(?: \[[A-Z]+\])?(?:, (.*?))?</a>[\n\r\t ]*</li>'.format(re.escape(lemmas_string)), content)
                if len(parsed_lexical_categories) != 1:
                    print(todo_id)
                    print(parsed_lexical_categories)
                    print('<li class="motActif">[\n\r\t ]*<a href="../article/[A-Z0-9-]+">{}(?: \[[A-Z]+\])?(?:, (.*?))?</a>[\n\r\t ]*</li>'.format(re.escape(lemmas_string)))
                    exit()
                parsed_lexical_categories = parsed_lexical_categories[0]
                if parsed_lexical_categories == 'abrév.':
                    matched_lexical_categories.add(dico.ABBREVIATION)
                elif parsed_lexical_categories in ('adj.', 'adj. f.', 'adj. m.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                elif parsed_lexical_categories in ('adj. et n.', 'n. et adj.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et n. f.', 'n. f. et adj.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et n. m.', 'n. m. et adj.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'n.':
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n. f.', 'n. f. inv.', 'n. f. pl.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n. m.', 'n. m. inv.', 'n. m. pl.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adv.', 'adv. de lieu'):
                    matched_lexical_categories.add(dico.ADVERB)
                elif parsed_lexical_categories == 'adv. et n. m.':
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'interj.':
                    matched_lexical_categories.add(dico.INTERJECTION)
                elif parsed_lexical_categories in ('interj. et n. m.', 'interj. et n. m. inv.'):
                    matched_lexical_categories.add(dico.INTERJECTION)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'loc.':
                    matched_lexical_categories.add(dico.LOCUTION)
                elif parsed_lexical_categories == 'loc. adj.':
                    matched_lexical_categories.add(dico.LOCUTION_ADJECTIVAL)
                elif parsed_lexical_categories == 'loc. adv.':
                    matched_lexical_categories.add(dico.LOCUTION_ADVERBIAL)
                elif parsed_lexical_categories == 'loc. adv. ou adj.':
                    matched_lexical_categories.add(dico.LOCUTION_ADJECTIVAL)
                    matched_lexical_categories.add(dico.LOCUTION_ADVERBIAL)
                elif parsed_lexical_categories == 'prép.':
                    matched_lexical_categories.add(dico.PREPOSITION)
                elif parsed_lexical_categories == 'symb.':
                    matched_lexical_categories.add(dico.CHEMICAL_SYMBOL)
                elif parsed_lexical_categories in ('v. intr.', 'v. tr.', 'v. intr. et tr.', 'v. tr. et intr.', 'v. tr. et pron.', 'v. pron.', 'v. tr., intr. et pron.', 'v. intr. et pron. impers.'):
                    matched_lexical_categories.add(dico.VERB)
                elif parsed_lexical_categories == '':
                    pass
                else:
                    print(todo_id)
                    print(parsed_lexical_categories)
                    exit()
                for lemma in matched_lemmas:
                    for lexical_category in matched_lexical_categories:
                        csvwriter.writerow([todo_id, lemma, lexical_category])


if __name__ == '__main__':
    main()
