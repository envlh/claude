import json
import re
import unidecode

from dico import Dico
from candidate import Candidate


class LeRobert(Dico):

    def __init__(self, db, offline=False):
        super().__init__(db, offline)

    def get_property_id(self):
        return 'P10338'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L28311 } . # led
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P10338 [] }
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
        return 'https://dictionnaire.lerobert.com/definition/{}'

    def infer_id(self, lemma):
        return re.sub(r'[^a-z]', '-', unidecode.unidecode(lemma).lower()).strip().strip('-')

    def parse_content(self, content, inferred_id):
        candidates = set()
        for h3 in re.findall(re.compile('<h3>(.*?)</h3>', re.DOTALL), content):
            # multiple sounds
            h3_cleaned = re.sub(re.compile('<span class="d_sound_sep"> \\| </span>', re.DOTALL), '', h3)
            # sound
            h3_cleaned = re.sub(re.compile('<span class="d_sound_cont"><sound.*?sound></span>', re.DOTALL), '', h3_cleaned)
            # nom déposé
            h3_cleaned = re.sub(re.compile('<span class="d_etm">\\(nom déposé\\)</span>', re.DOTALL), '', h3_cleaned)
            # misc html
            h3_cleaned = re.sub(re.compile('<span class="notBold">Définition de </span>', re.DOTALL), '', h3_cleaned)
            match = re.search(re.compile('^(.*?)<span class="d_cat">(.*?)</span>', re.DOTALL), h3_cleaned.strip(' \n\t'))
            if match is not None:
                lexical_categories = set()
                genders = set()
                lemmas = set(re.split('(?:, )|(?: <span class="d_mta">ou</span> )', match.group(1).strip()))
                matched_lexical_categories = re.split('(?:, )|(?: <span class="d_x">et</span> )', match.group(2).strip())
                for matched_lexical_category in matched_lexical_categories:
                    if matched_lexical_category in ('élément', 'symbole', 'nom'):
                        lexical_categories.add(self.IGNORE)
                    elif matched_lexical_category in ('adjectif', 'adjectif invariable'):
                        lexical_categories.add(self.ADJECTIVE)
                    elif matched_lexical_category in ('adverbe', 'adverbe de lieu', 'adverbe de négation'):
                        lexical_categories.add(self.ADVERB)
                    elif matched_lexical_category == 'conjonction':
                        lexical_categories.add(self.CONJUNCTION)
                    elif matched_lexical_category == 'interjection':
                        lexical_categories.add(self.INTERJECTION)
                    elif matched_lexical_category in ('pronom personnel', 'pronom personnel invariable', 'pronom personnel féminin', 'pronom personnel masculin'):
                        lexical_categories.add(self.PERSONAL_PRONOUN)
                    elif matched_lexical_category == 'locution adverbiale':
                        lexical_categories.add(self.LOCUTION_ADVERBIAL)
                    elif matched_lexical_category in ('nom féminin', 'nom féminin invariable', 'nom féminin pluriel'):
                        lexical_categories.add(self.NOUN)
                        genders.add(self.FEMININE)
                    elif matched_lexical_category in ('nom masculin', 'nom masculin invariable', 'nom masculin pluriel'):
                        lexical_categories.add(self.NOUN)
                        genders.add(self.MASCULINE)
                    elif matched_lexical_category in ('verbe', 'verbe impersonnel', 'verbe intransitif', 'verbe intransitif impersonnel', 'verbe pronominal', 'verbe transitif', 'verbe transitif indirect'):
                        lexical_categories.add(self.VERB)
                    else:
                        self.add_unknown_lexical_category(matched_lexical_category)
                for lemma in lemmas:
                    for lexical_category in lexical_categories:
                        candidates.add(Candidate(inferred_id, lemma, lexical_category, genders))
        return candidates

    def get_id_from_redirect(self, r):
        redirect_id = json.loads(r['headers'])['location'][45:]
        if len(redirect_id) >= 1:
            return redirect_id
        return None

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 2|Le Robert import]]'
