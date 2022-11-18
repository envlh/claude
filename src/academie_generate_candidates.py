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
                # if no match, try lemma without ,...
                # example: https://www.dictionnaire-academie.fr/article/A9A2808
                if len(parsed_lexical_categories) != 1:
                    parsed_lexical_categories = re.findall('<li class="motActif">[\n\r\t ]*<a href="../article/[A-Z0-9-]+">{}(?: \[[A-Z]+\])?(?:, (.*?))?</a>[\n\r\t ]*</li>'.format(re.escape(re.sub(',.*?$', '', lemmas_string))), content)
                if len(parsed_lexical_categories) != 1:
                    print(todo_id)
                    print(parsed_lexical_categories)
                    print('<li class="motActif">[\n\r\t ]*<a href="../article/[A-Z0-9-]+">{}(?: \[[A-Z]+\])?(?:, (.*?))?</a>[\n\r\t ]*</li>'.format(re.escape(lemmas_string)))
                    exit()
                parsed_lexical_categories = parsed_lexical_categories[0]
                if parsed_lexical_categories == 'abrév.':
                    matched_lexical_categories.add(dico.ABBREVIATION)
                elif parsed_lexical_categories in ('adj.', 'adj. f.', 'adj. m.', 'adj. inv.', 'adj. inv. en genre', 'adj. qualificatif', '-ale, adj.', 'adj. m. pl.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                elif parsed_lexical_categories == 'adj. dém.':
                    matched_lexical_categories.add(dico.ADJECTIVE_DEMONSTRATIVE)
                elif parsed_lexical_categories == 'adj. indéf. sing.':
                    matched_lexical_categories.add(dico.ADJECTIVE_INDEFINITE)
                elif parsed_lexical_categories in ('article', 'articles'):
                    matched_lexical_categories.add(dico.ARTICLE)
                elif parsed_lexical_categories in ('adj. et n.', 'n. et adj.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et n. f.', 'n. f. et adj.', 'n. f. et adj. inv.', 'adj. f. et n. f.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et n. m.', 'n. m. et adj.', 'n. m. et adj. inv.', 'n. et adj. m.', 'adj. et n. m. pl.', 'adj. m. et n. m.', 'adj. inv. et n. m.', 'n. m. et adj. m.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n.', 'n. inv.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n. f.', 'n. f. inv.', 'n. f. sing.', 'n. f. pl.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n. m.', 'n. m. inv.', 'n. m. sing.', 'n. m. pl.', 'n. m. composé inv.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('n. m. ou f. inv.', 'n. m., quelquefois f.', 'n. f. ou m.', 'n. m. et f.', 'n. m. parfois f.', 'n. m. et n. f.', 'n. f. ou parfois m.', 'n. m. ou f.'):
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adv.', 'adv. de lieu', 'adv. de quantité', 'adv. de temps', 'adv. de manière', 'adv. de négation'):
                    matched_lexical_categories.add(dico.ADVERB)
                elif parsed_lexical_categories == 'adv. et conj.':
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.CONJUNCTION)
                elif parsed_lexical_categories == 'adv. et n. m.':
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'adj. numér. ordinal':
                    matched_lexical_categories.add(dico.NUMERAL)
                elif parsed_lexical_categories in ('adj. numér. et n. m.', 'adj. numér. et n. m. inv.', 'adj. numér. cardinal inv. et n. m. inv.'):
                    matched_lexical_categories.add(dico.NUMERAL)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et adv.', 'adj. m. et adv.', 'adv. et adj. inv.'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.ADVERB)
                elif parsed_lexical_categories == 'conj. de coord.':
                    matched_lexical_categories.add(dico.CONJUNCTION_COORDINATING)
                elif parsed_lexical_categories == 'conj. de coord. et adv.':
                    matched_lexical_categories.add(dico.CONJUNCTION_COORDINATING)
                    matched_lexical_categories.add(dico.ADVERB)
                elif parsed_lexical_categories == 'interj.':
                    matched_lexical_categories.add(dico.INTERJECTION)
                elif parsed_lexical_categories in ('interj. et n. m.', 'interj. et n. m. inv.', 'n. m. et interj.'):
                    matched_lexical_categories.add(dico.INTERJECTION)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('loc.', 'loc. inv.'):
                    matched_lexical_categories.add(dico.LOCUTION)
                elif parsed_lexical_categories in ('loc. adj.', '-ée, loc. adj.', '-use, loc. adj.', 'ci-jointe, loc. adj.'):
                    matched_lexical_categories.add(dico.LOCUTION_ADJECTIVAL)
                elif parsed_lexical_categories == 'loc. adv.':
                    matched_lexical_categories.add(dico.LOCUTION_ADVERBIAL)
                elif parsed_lexical_categories == 'loc. verb.':
                    matched_lexical_categories.add(dico.LOCUTION_VERBAL)
                elif parsed_lexical_categories in ('loc. adv. ou adj.', 'loc. adj. ou adv.'):
                    matched_lexical_categories.add(dico.LOCUTION_ADJECTIVAL)
                    matched_lexical_categories.add(dico.LOCUTION_ADVERBIAL)
                elif parsed_lexical_categories == 'préf.':
                    matched_lexical_categories.add(dico.PREFIX)
                elif parsed_lexical_categories == 'prép.':
                    matched_lexical_categories.add(dico.PREPOSITION)
                elif parsed_lexical_categories in ('pron. dém.', 'pr. dém. neutre inv.', 'pr. dém. neutre', 'pr. dém.'):
                    matched_lexical_categories.add(dico.PRONOUN_DEMONSTRATIVE)
                elif parsed_lexical_categories in ('pr. indéf. inv.', 'pr. indéf. sing.'):
                    matched_lexical_categories.add(dico.PRONOUN_INDEFINITE)
                elif parsed_lexical_categories in ('pr. rel.', 'pr. rel. inv.'):
                    matched_lexical_categories.add(dico.PRONOUN_RELATIVE)
                elif parsed_lexical_categories == 'pr. rel. ou interr.':
                    matched_lexical_categories.add(dico.PRONOUN_RELATIVE)
                    matched_lexical_categories.add(dico.PRONOUN_INTERROGATIVE)
                elif parsed_lexical_categories == 'sigle':
                    matched_lexical_categories.add(dico.SIGLE)
                elif parsed_lexical_categories == 'symb.':
                    matched_lexical_categories.add(dico.CHEMICAL_SYMBOL)
                elif parsed_lexical_categories in ('v. intr.', 'v. tr.', 'v. intr. et tr.', 'v. tr. et intr.', 'v. tr. et pron.', 'v. pron.', 'v. tr., intr. et pron.', 'v. intr. et pron. impers.', 'v. tr., intr. ou pron.', 'v. intr. et pron.', 'v. impers.', 'v. intr. ou pron.', 'v. tr. et intr. ou pron.', 'v. tr., pron. et intr.', 'v. tr. et auxiliaire', 'v. intr., tr. et pron.', 'v. pron. et tr.', 'v. impers. et intr.'):
                    matched_lexical_categories.add(dico.VERB)
                elif parsed_lexical_categories == 'interj., adj. et n. f.':
                    matched_lexical_categories.add(dico.INTERJECTION)
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'suff. et n. m. inv.':
                    matched_lexical_categories.add(dico.SUFFIX)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'prép. et adv.':
                    matched_lexical_categories.add(dico.PREPOSITION)
                    matched_lexical_categories.add(dico.ADVERB)
                elif parsed_lexical_categories == 'v. tr. et loc. conj.':
                    matched_lexical_categories.add(dico.VERB)
                    matched_lexical_categories.add(dico.LOCUTION_CONJUNCTIVE)
                elif parsed_lexical_categories == 'adj., prép. et n.':
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.PREPOSITION)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == 'prép., adv. et n. m.':
                    matched_lexical_categories.add(dico.PREPOSITION)
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories in ('adj. et pr. indéf.', 'adj. et pr. indéf.; adj. qualificatif'):
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.PRONOUN_INDEFINITE)
                elif parsed_lexical_categories in ('adj. indéf. et pr. indéf. pl.', 'adj. indéf. pl. et pr. indéf. pl.'):
                    matched_lexical_categories.add(dico.ADJECTIVE_INDEFINITE)
                    matched_lexical_categories.add(dico.PRONOUN_INDEFINITE)
                elif parsed_lexical_categories in ('adv., n. m. et adj. inv.', 'adj. m., adv. et n. m.', 'adj., adv. et n. m.'):
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.NOUN)
                    matched_lexical_categories.add(dico.ADJECTIVE)
                elif parsed_lexical_categories == 'adj., adv. et n.':
                    matched_lexical_categories.add(dico.ADJECTIVE)
                    matched_lexical_categories.add(dico.ADVERB)
                    matched_lexical_categories.add(dico.NOUN)
                elif parsed_lexical_categories == '':
                    pass
                else:
                    print(todo_id)
                    print(parsed_lexical_categories)
                    # exit()
                for lemma in matched_lemmas:
                    for lexical_category in matched_lexical_categories:
                        csvwriter.writerow([todo_id, lemma, lexical_category])


if __name__ == '__main__':
    main()
