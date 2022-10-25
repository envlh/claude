import json
import re

from dico import Dico
from candidate import Candidate


class Larousse(Dico):

    def __init__(self, db, offline=False):
        super().__init__(db, offline)

    def get_property_id(self):
        return 'P11118'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L11954 } . # aujourd'hui
  # VALUES ?lexeme { wd:L13180 } . # complètement
  # VALUES ?lexeme { wd:L641287 } . # gelée royale
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P11118 [] }
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
        return 'https://www.larousse.fr/dictionnaires/francais/{}'

    def infer_id(self, lemma):
        return lemma.lower().replace('’', '\'')

    def parse_content(self, content, inferred_id):
        inferred_id = re.sub('#.*?$', '', re.sub('^.*?/', '', inferred_id))
        candidates = set()
        for entry in re.findall(re.compile('<div class="Zone-Entree[0-9]* header-article" id="[0-9]+">.*?</div>', re.DOTALL), content):
            entry_id = re.findall('id="([0-9]+)">', entry)
            lemma = re.findall('</audio>(.*?)</h2>', entry)
            parsed_lexical_category = re.findall('<p class="CatgramDefinition">(.*?)</p>', entry)
            genders = set()
            if len(entry_id) == 1 and len(lemma) == 1 and len(parsed_lexical_category) == 1:
                entry_id = entry_id[0]
                lemmas = lemma[0].split(', ')
                parsed_lexical_category = parsed_lexical_category[0]
                parsed_lexical_category = re.sub('<a .*?</a>', '', parsed_lexical_category)
                parsed_lexical_category = re.sub('<span .*?</span>', '', parsed_lexical_category)
                parsed_lexical_category = parsed_lexical_category.strip()
                matched_lexical_categories = set()
                if parsed_lexical_category in ('adverbe', 'adverbe exclamatif', 'adverbe interrogatif', 'adverbe (sans trait d\'union)', 'adverbe interrogatif et exclamatif'):
                    matched_lexical_categories.add(self.ADVERB)
                elif parsed_lexical_category in ('adverbe et adjectif', 'adverbe et adjectif invariable'):
                    matched_lexical_categories.add(self.ADVERB)
                    matched_lexical_categories.add(self.ADJECTIVE)
                elif parsed_lexical_category in ('adjectif', 'adjectif invariable', 'adjectif féminin', 'adjectif masculin', 'adjectif qualificatif'):
                    matched_lexical_categories.add(self.ADJECTIVE)
                elif parsed_lexical_category in ('adjectif numéral cardinal invariable', 'adjectif numéral cardinal', 'adjectif numéral invariable', 'adjectif numéral ordinal', 'adjectif numéral'):
                    matched_lexical_categories.add(self.NUMERAL)
                elif parsed_lexical_category == 'adjectif numéral ordinal et nom':
                    matched_lexical_categories.add(self.NUMERAL)
                    matched_lexical_categories.add(self.NOUN)
                elif parsed_lexical_category == 'adjectif numéral cardinal et nom masculin invariable':
                    matched_lexical_categories.add(self.NUMERAL)
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.MASCULINE)
                elif parsed_lexical_category in ('adjectif et nom', 'adjectif et nom invariable', 'nom et adjectif'):
                    matched_lexical_categories.add(self.ADJECTIVE)
                    matched_lexical_categories.add(self.NOUN)
                elif parsed_lexical_category in ('adjectif et nom féminin', 'adjectif féminin et nom féminin'):
                    matched_lexical_categories.add(self.ADJECTIVE)
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.FEMININE)
                elif parsed_lexical_category in ('adjectif et nom masculin', 'adjectif et nom masculin invariable', 'adjectif invariable et nom masculin invariable', 'adjectif invariable et nom masculin', 'nom masculin et adjectif', 'nom masculin invariable ou nom masculin'):
                    matched_lexical_categories.add(self.ADJECTIVE)
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.MASCULINE)
                elif parsed_lexical_category == 'conjonction':
                    matched_lexical_categories.add(self.CONJUNCTION)
                elif parsed_lexical_category == 'interjection':
                    matched_lexical_categories.add(self.INTERJECTION)
                elif parsed_lexical_category == 'locution adverbiale':
                    matched_lexical_categories.add(self.LOCUTION_ADVERBIAL)
                elif parsed_lexical_category in ('nom féminin', 'nom féminin invariable', 'nom féminin singulier', 'nom féminin pluriel'):
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.FEMININE)
                elif parsed_lexical_category in ('nom masculin', 'nom masculin invariable', 'nom masculin singulier', 'nom masculin pluriel'):
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.MASCULINE)
                elif parsed_lexical_category in ('nom féminin ou masculin', 'nom masculin ou nom féminin'):
                    matched_lexical_categories.add(self.NOUN)
                    genders.add(self.FEMININE)
                    genders.add(self.MASCULINE)
                elif parsed_lexical_category == 'préposition':
                    matched_lexical_categories.add(self.PREPOSITION)
                elif parsed_lexical_category == 'préposition ou adverbe':
                    matched_lexical_categories.add(self.PREPOSITION)
                    matched_lexical_categories.add(self.ADVERB)
                elif parsed_lexical_category in ('verbe auxiliaire', 'verbe impersonnel', 'verbe impersonnel et transitif', 'verbe intransitif', 'verbe intransitif et verbe transitif', 'verbe intransitif et verbe transitif indirect', 'verbe intransitif et verbe impersonnel', 'verbe passif', 'verbe pronominal', 'verbe pronominal et verbe impersonnel', 'verbe pronominal impersonnel', 'verbe transitif', 'verbe\xa0transitif', 'verbe transitif employé absolument', 'verbe transitif et verbe transitif indirect', 'verbe transitif et intransitif', 'verbe transitif et verbe intransitif', 'verbe transitif indirect', 'verbe transitif ou verbe transitif indirect', 'verbe transitif indirect et verbe impersonnel'):
                    matched_lexical_categories.add(self.VERB)
                else:
                    self.add_unknown_lexical_category(parsed_lexical_category)
                for lexical_category in matched_lexical_categories:
                    for lemma in lemmas:
                        candidates.add(Candidate('{}#{}'.format(inferred_id, entry_id), lemma, lexical_category, genders))
        for entry in re.findall(re.compile('<li class="Locution" id="[0-9]+">[\r\n\t ]*<h2 class="AdresseLocution">.*?, </h2>', re.DOTALL), content):
            entry_id = re.findall('id="([0-9]+)">', entry)
            lemma = re.findall('"AdresseLocution">(.*?), </h2>', entry)
            if len(entry_id) == 1 and len(lemma) == 1:
                entry_id = entry_id[0]
                lemma = lemma[0].lower()
                candidates.add(Candidate('{}#{}'.format(inferred_id, entry_id), lemma, self.LOCUTION_NOMINAL, set()))
        # print(candidates)
        return candidates

    def get_id_from_redirect(self, r):
        redirect_id = re.sub('#.*?$', '', json.loads(r['headers'])['Location'][24:])
        if len(redirect_id) >= 1:
            return redirect_id
        return None

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
