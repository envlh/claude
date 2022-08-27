import json
import re
import urllib.parse

from dico import Dico


class Littre(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        return 'P7724'

    def get_lexemes_to_crawl_query(self):
        return '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategoryLabel (GROUP_CONCAT(?genderLabel_ ; separator=",") AS ?genderLabel) {
  # VALUES ?lexeme { wd:L621228 } .
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P7724 [] }
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
LIMIT 100000
'''

    def get_url(self):
        return 'https://www.littre.org/definition/{}'

    def infer_id(self, lemma):
        return lemma.replace('œ', 'oe')

    def is_matching(self, content, lemma, lexical_category, gender):
        match = re.search(re.compile('<section class="definition"><h2(?: class="[a-z]*")?>(.*?)</h2>.*?<div class="entete">.*?<b>(.*?)</b>', re.DOTALL), content)
        if match is not None:
            lem_match = match.group(1).strip()
            lemmas_match = lem_match.split(', ')
            for i in range(1, len(lemmas_match)):
                first_char = lemmas_match[i][:1]
                position = lemmas_match[0].rfind(first_char)
                lemmas_match[i] = lemmas_match[0][:position] + lemmas_match[i]
            lexcat_match = match.group(2)
            if lemma in lemmas_match:
                if lexical_category == 'nom':
                    if gender == 'féminin' and lexcat_match == '<abbr title="substantif féminin">s. f.</abbr>':
                        return True
                    if gender == 'masculin' and lexcat_match == '<abbr title="substantif masculin">s. m.</abbr>':
                        return True
                    if gender in ('féminin,masculin', 'masculin,féminin') and lexcat_match == '<abbr title="substantif masculin et féminin">s. m. et f.</abbr>':
                        return True
                    if len(lemmas_match) == 2 and gender in ('féminin', 'masculin') and lexcat_match == '<abbr title="substantif masculin et féminin">s. m. et f.</abbr>':
                        return True
                if lexical_category == 'verbe' and lexcat_match in ('<abbr title="verbe neutre, notion grammaticale désuete">v. n.</abbr>', '<abbr title="verbe transitif, anciennement appelé verbe actif">v. a.</abbr>'):
                    return True
                if lexical_category == 'adjectif' and lexcat_match == '<abbr title="adjectif">adj.</abbr>':
                    return True
                if lexical_category == 'adverbe' and lexcat_match == '<abbr title="adverbe">adv.</abbr>':
                    return True
            # print(lemma, lexical_category, gender, lem_match, lexcat_match)
        # print(lemma, lexical_category, gender, match)
        return False

    def get_id_from_redirect(self, r):
        redirect_id = urllib.parse.unquote(json.loads(r['headers'])['Location'][12:])
        if len(redirect_id) >= 1:
            return redirect_id
        return None

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 3|French dictionaries import]]'
