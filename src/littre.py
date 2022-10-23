import json
import re
import urllib.parse

from dico import Dico
from candidate import Candidate


class Littre(Dico):

    def __init__(self, db, offline=False):
        super().__init__(db, offline)

    def get_property_id(self):
        return 'P7724'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L621228 } .
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P7724 [] }
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
        return 'https://www.littre.org/definition/{}'

    def infer_id(self, lemma):
        return lemma.replace('œ', 'oe')

    def parse_content(self, content, inferred_id):
        candidates = set()
        match = re.search(re.compile('<section class="definition"><h2(?: class="[a-z]*")?>(.*?)</h2>.*?<div class="entete">.*?<b>(.*?)</b>', re.DOTALL), content)
        if match is not None:
            lem_match = match.group(1).strip()
            lemmas_match = lem_match.split(', ')
            for i in range(1, len(lemmas_match)):
                first_char = lemmas_match[i][:1]
                position = lemmas_match[0].rfind(first_char)
                lemmas_match[i] = lemmas_match[0][:position] + lemmas_match[i]
            matched_lexical_category = match.group(2)
            lexical_categories = set()
            genders = set()
            if matched_lexical_category in ('<abbr title="substantif féminin">s. f.</abbr>', '<abbr title="substantif féminin">S. f.</abbr>', '<abbr title="substantif féminin pluriel">s. f. pl.</abbr>'):
                lexical_categories.add(self.NOUN)
                genders.add(self.FEMININE)
            elif matched_lexical_category in ('<abbr title="substantif masculin">s. m.</abbr>', '<abbr title="substantif masculin">S. m.</abbr>', '<abbr title="substantif masculin pluriel">s. m. plur.</abbr>', '<abbr title="substantif masculin pluriel">s. m. pl.</abbr>'):
                lexical_categories.add(self.NOUN)
                genders.add(self.MASCULINE)
            elif matched_lexical_category == '<abbr title="substantif masculin et féminin">s. m. et f.</abbr>':
                lexical_categories.add(self.NOUN)
                genders.add(self.FEMININE)
                genders.add(self.MASCULINE)
            elif matched_lexical_category in ('<abbr title="verbe neutre, notion grammaticale désuete">v. n.</abbr>', '<abbr title="verbe neutre, notion grammaticale désuete">V. n.</abbr>', '<abbr title="verbe transitif, anciennement appelé verbe actif">v. a.</abbr>', '<abbr title="verbe transitif, anciennement appelé verbe actif">V. a.</abbr>', '<abbr title="verbe pronominal, anciennement appelé verbe réflexif">v. réfl.</abbr>'):
                lexical_categories.add(self.VERB)
            elif matched_lexical_category in ('<abbr title="adjectif">adj.</abbr>', '<abbr title="adjectif">adj.</abbr>', '<abbr title="adjectif féminin">adj. f.</abbr>', '<abbr title="adjectif masculin">adj. m.</abbr>'):
                lexical_categories.add(self.ADJECTIVE)
            elif matched_lexical_category == '<abbr title="adverbe">adv.</abbr>':
                lexical_categories.add(self.ADVERB)
            elif matched_lexical_category == '<abbr title="locution adverbiale">loc. adv.</abbr>':
                lexical_categories.add(self.LOCUTION_ADVERBIAL)
            else:
                self.add_unknown_lexical_category(matched_lexical_category)
            for lemma in lemmas_match:
                for lexical_category in lexical_categories:
                    candidates.add(Candidate(inferred_id, lemma, lexical_category, genders))
        return candidates

    def get_id_from_redirect(self, r):
        redirect_id = urllib.parse.unquote(json.loads(r['headers'])['Location'][12:])
        if len(redirect_id) >= 1:
            return redirect_id
        return None

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
