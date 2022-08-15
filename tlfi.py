from dico import Dico


class Tlfi(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        return 'P7722'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategoryLabel (GROUP_CONCAT(?genderLabel_ ; separator=",") AS ?genderLabel) {
  # VALUES ?lexeme { wd:L621228 } .
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P7722 [] }
  BIND((NOW() - "P2D"^^xsd:duration) AS ?dateLimit)
  # FILTER (?dateModified < ?dateLimit) .
  FILTER (?lexicalCategory != wd:Q162940) . # diacritique
  FILTER (?lexicalCategory != wd:Q9788) . # lettre
  FILTER (?lexicalCategory != wd:Q147276) . # nom propre
  ?lexicalCategory rdfs:label ?lexicalCategoryLabel .
  FILTER(LANG(?lexicalCategoryLabel) = "fr") .
  OPTIONAL {
    ?lexeme wdt:P5185 ?gender .
    ?gender rdfs:label ?genderLabel_ .
    FILTER(LANG(?genderLabel_) = "fr")
  }
}
GROUP BY ?lexeme ?lemma ?lexicalCategoryLabel
LIMIT 10
'''

    def get_url(self):
        return 'https://www.cnrtl.fr/definition/{}'

    def infer_id(self, lemma):
        return lemma.lower()

    def is_matching(self, content, lemma, lexical_category, gender):
        inferred_id = self.infer_id(lemma)
        return 'sendRequest(5,\'/definition/{}//0\')'.format(inferred_id) in content and 'sendRequest(5,\'/definition/{}//1\')'.format(inferred_id) not in content

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
