import re

from dico import Dico
from candidate import Candidate


class Cordial(Dico):

    def __init__(self, db, offline=False):
        super().__init__(db, offline)

    def get_property_id(self):
        return 'P11178'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L2330 } . # tour
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P11178 [] }
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
        return 'https://www.cordial.fr/dictionnaire/definition/{}.php'

    def infer_id(self, lemma):
        return lemma.lower()

    def parse_content(self, content, inferred_id):
        candidates = set()
        lemmas = re.findall('<h2 class="synapse-title-def">Définition de (.*?)[\n\t ]*</h2>', content)
        parsed_lexical_categories = re.findall('class="categ_complete"><i>(.*?)</i>', content)
        genders = set()
        matched_lexical_categories = set()
        for lemma in lemmas:
            lemma = lemma.strip()
            for parsed_lexical_category in parsed_lexical_categories:
                if parsed_lexical_category in ('adjectif singulier invariant en genre', 'adjectif invariant en genre et en nombre', 'adjectif masculin singulier', 'adjectif masculin invariant en nombre', 'adjectif indéfini', 'adjectif interrogatif'):
                    matched_lexical_categories.add(self.ADJECTIVE)
                elif parsed_lexical_category in ('adjectif cardinal', 'adjectif ordinal'):
                    matched_lexical_categories.add(self.NUMERAL)
                elif parsed_lexical_category == 'adverbe':
                    matched_lexical_categories.add(self.ADVERB)
                elif parsed_lexical_category == 'interjection':
                    matched_lexical_categories.add(self.INTERJECTION)
                elif parsed_lexical_category in ('nom singulier invariant en genre', 'nom invariant en genre et en nombre', 'nom pluriel invariant en genre'):
                    matched_lexical_categories.add(self.NOUN)
                elif parsed_lexical_category in ('nom féminin singulier', 'nom féminin pluriel', 'nom féminin invariant en nombre'):
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.FEMININE)
                elif parsed_lexical_category in ('nom masculin singulier', 'nom masculin pluriel', 'nom masculin invariant en nombre'):
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.MASCULINE)
                elif parsed_lexical_category == 'préposition':
                    matched_lexical_categories.add(self.PREPOSITION)
                elif parsed_lexical_category == 'pronom personnel':
                    matched_lexical_categories.add(self.PERSONAL_PRONOUN)
                elif parsed_lexical_category in ('verbe', 'verbe pronominal'):
                    matched_lexical_categories.add(self.VERB)
                else:
                    self.add_unknown_lexical_category(parsed_lexical_category)
            for lexical_category in matched_lexical_categories:
                candidates.add(Candidate(inferred_id, lemma, lexical_category, genders))
        return candidates

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
