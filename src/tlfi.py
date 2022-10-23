import re

from dico import Dico
from candidate import Candidate


class Tlfi(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        return 'P7722'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L2330 } . # tour
  # VALUES ?lexeme { wd:L620286 } . # informaticien
  # VALUES ?lexeme { wd:L620287 } . # informaticienne
  # VALUES ?lexeme { wd:L20303 } . # ångström
  # VALUES ?lexeme { wd:L2242 } . # parler (verbe)
  # VALUES ?lexeme { wd:L9217 } . # grand (adjectif)
  # VALUES ?lexeme { wd:L10098 } . # petit (adjectif)
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P7722 [] }
  # BIND((NOW() - "P2D"^^xsd:duration) AS ?dateLimit)
  # FILTER (?dateModified < ?dateLimit) .
  FILTER (?lexicalCategory != wd:Q162940) . # diacritique
  FILTER (?lexicalCategory != wd:Q9788) . # lettre
  FILTER (?lexicalCategory != wd:Q147276) . # nom propre
  OPTIONAL { ?lexeme wdt:P5185 ?gender }
}
GROUP BY ?lexeme ?lemma ?lexicalCategory
LIMIT 100000
'''

    def get_url(self):
        return 'https://www.cnrtl.fr/definition/{}'

    def infer_id(self, lemma):
        return lemma.lower()

    def parse_content(self, content, inferred_id):
        candidates = set()
        matches = re.findall(r'<a href="#" onclick="return sendRequest\(5,\'/definition/(.*?)//([0-9]+)\'\);"><span>(.*?)(?:<sup>[0-9]+</sup>)?</span>(.*?)</a>', content)
        for match in matches:
            # parsed id
            if len(matches) > 1:
                parsed_id = '{}/{}'.format(inferred_id, match[1])
            else:
                parsed_id = inferred_id
            # lemmas
            lemmas = set()
            matched_lemmas = re.sub(r'<sup>[0-9]+</sup>', '', match[2]).lower().split(', ')
            for lemma in matched_lemmas:
                if lemma[:1] != '-':
                    lemmas.add(lemma)
                else:
                    first_char = lemma[1:2]
                    position = matched_lemmas[0].rfind(first_char)
                    lemmas.add(matched_lemmas[0][:position] + lemma[1:])
            # lexical category and gender
            lexical_categories = set()
            genders = set()
            matched_lexical_category = match[3].strip(' ,')
            if matched_lexical_category in ('adjectif', 'substantif', 'élément formant'):
                lexical_categories.add(self.IGNORE)
            elif matched_lexical_category in ('subst.', 'subst. inv.'):
                lexical_categories.add(self.NOUN)
            elif matched_lexical_category in ('subst fém.', 'subst. fém.', 'subst.fém.', 'subst. fém. sing.', 'subst. fém. plur.'):
                lexical_categories.add(self.NOUN)
                genders.add(self.FEMININE)
            elif matched_lexical_category in ('subst. masc.', 'subst. masc.;', 'subst. masc. sing.', 'subst. masc. plur.', 'subst. masc.; plur.', 'subst. masc. inv.', 'subst. masc. et inv.', 'subst. masc. invar.', '2, subst. masc.'):
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('subst. masc. ou fém.', 'subst. masc. (except. fém.)'):
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
                genders.add(self.FEMININE)
            elif matched_lexical_category in ('subst. et adj.', 'adj. et subst.', 'adj. et subst. invar.', 'part. prés., adj. et subst.', 'part. passé, adj. et subst.'):
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.NOUN)
            elif matched_lexical_category in ('adj. et subst. fém.', 'subst. fém. et adj.', 'subst. fém. et adj. inv.', 'subst. fém. et adj. fém.'):
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.NOUN)
                genders.add(self.FEMININE)
            elif matched_lexical_category in ('subst. masc. et adj.', 'subst. masc. et adj. masc.', 'part. passé, adj. et subst. masc.', 'adj. et subst. masc. inv.', 'part. passé, adj. et subst. masc. sing.', 'adj. et subst. masc.', 'adj. et subst. masc. inv', 'adj. inv. et subst. masc.', 'adj. et subst. masc. plur.', 'part. prés., adj. et subst. masc.'):
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('adj.', 'adj.;', 'adj. inv.', 'part. prés. et adj.', 'part. passé et adj.', '1, adj.'):
                lexical_categories.add(self.ADJECTIVE)
            elif matched_lexical_category in ('adv.', 'adv. de nég.'):
                lexical_categories.add(self.ADVERB)
            elif matched_lexical_category == 'loc. adv.':
                lexical_categories.add(self.LOCUTION_ADVERBIAL)
            elif matched_lexical_category == 'subst. masc. et adv.':
                lexical_categories.add(self.NOUN)
                lexical_categories.add(self.ADVERB)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('conj.', 'conj. de coordination.'):
                lexical_categories.add(self.CONJUNCTION)
            elif matched_lexical_category == 'adv. et conj.':
                lexical_categories.add(self.ADVERB)
                lexical_categories.add(self.CONJUNCTION)
            elif matched_lexical_category == 'adj. et adv.':
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.ADVERB)
            elif matched_lexical_category in ('adj., subst. et adv.', 'adj., adv. et subst.', 'adv., adj. et subst.'):
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.NOUN)
                lexical_categories.add(self.ADVERB)
            elif matched_lexical_category in ('adj., subst. masc. et adv.', 'part. prés., adj. masc., subst. masc. et adv.'):
                lexical_categories.add(self.ADJECTIVE)
                lexical_categories.add(self.NOUN)
                lexical_categories.add(self.ADVERB)
                genders.add(self.MASCULINE)
            elif matched_lexical_category == 'interj.':
                lexical_categories.add(self.INTERJECTION)
            elif matched_lexical_category == 'interj. et subst. fém.':
                lexical_categories.add(self.INTERJECTION)
                lexical_categories.add(self.NOUN)
                genders.add(self.FEMININE)
            elif matched_lexical_category == 'interj. et subst. masc.':
                lexical_categories.add(self.INTERJECTION)
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('prép.', 'formateur de loc. adv. ou prép.'):
                lexical_categories.add(self.PREPOSITION)
            elif matched_lexical_category == 'prép. et adv.':
                lexical_categories.add(self.PREPOSITION)
                lexical_categories.add(self.ADVERB)
            elif matched_lexical_category == 'prép., adv. et subst. masc.':
                lexical_categories.add(self.PREPOSITION)
                lexical_categories.add(self.ADVERB)
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('pron. pers.', 'pron. pers., 3epers., neutre sing., forme atone'):
                lexical_categories.add(self.PERSONAL_PRONOUN)
            elif matched_lexical_category in ('verbe', 'verbe.', 'verbe trans.', 'verbe trans. indir.', 'verbe intrans.', 'verbe intrans. et impers.', 'verbe pronom.', 'verbe (semi-)auxiliaire.', 'verbe auxil.', 'verbe substitut.', 'verbe trans. indir. et pronom.', 'verbe trans. et intrans.', 'verbe intrans. et trans.', 'verbe trans. et pronom.', 'verbe pronom. réfl.', 'verbe impers.', 'verbe trans. dir. et indir.', 'verbe intrans. et pronom.'):
                lexical_categories.add(self.VERB)
            elif matched_lexical_category == 'verbe trans. et subst. masc.':
                lexical_categories.add(self.VERB)
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            else:
                self.add_unknown_lexical_category(matched_lexical_category)
            for lemma in lemmas:
                for lexical_category in lexical_categories:
                    candidates.add(Candidate(parsed_id, lemma, lexical_category, genders))
        return candidates

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
