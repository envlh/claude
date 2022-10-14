from dico import Dico
from candidate import Candidate


class FavereauBR(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        return 'P11068'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategory (GROUP_CONCAT(?gender ; separator=",") AS ?genders) {
  # VALUES ?lexeme { wd:L3397 } . # ober
  ?lexeme dct:language wd:Q12107 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P11068 [] }
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
        return 'http://www.arkaevraz.net/dicobzh/index.php?b_lang=1&b_kw={}'

    def infer_id(self, lemma):
        return lemma.lower()

    def parse_content(self, content, inferred_id):
        candidates = set()
        if '<td valign=top>{} </td>'.format(inferred_id.upper()) in content:
            candidates.add(Candidate(inferred_id, inferred_id, self.ACCEPT_ALL, set()))
        return candidates

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
