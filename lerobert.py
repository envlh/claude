import json
import re
import unidecode

from dico import Dico


class LeRobert(Dico):

    def __init__(self, db):
        super().__init__(db)

    def get_property_id(self):
        return 'P10338'

    def get_lexemes_to_crawl_query(self):
        r = '''SELECT DISTINCT ?lexeme ?lemma ?lexicalCategoryLabel (GROUP_CONCAT(?genderLabel_ ; separator=",") AS ?genderLabel) {
  ?lexeme dct:language wd:Q150 ; wikibase:lemma ?lemma ; wikibase:lexicalCategory ?lexicalCategory ; schema:dateModified ?dateModified .
  FILTER NOT EXISTS { ?lexeme wdt:P10338 [] }
  BIND((NOW() - "P2D"^^xsd:duration) AS ?dateLimit)
  FILTER (?dateModified < ?dateLimit) .
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
        return r

    def get_url(self):
        return 'https://dictionnaire.lerobert.com/definition/{}'

    def infer_id(self, lemma):
        return re.sub(r'[^a-z]', '-', unidecode.unidecode(lemma).lower()).strip().strip('-')

    def is_matching(self, content, lemma, lexical_category, gender):
        valids = []
        for h3 in re.findall(re.compile('<h3>(.*?)</h3>', re.DOTALL), content):
            # multiple sounds
            h3_cleaned = re.sub(re.compile('<span class="d_sound_sep"> \\| </span>', re.DOTALL), '', h3)
            # sound
            h3_cleaned = re.sub(re.compile('<span class="d_sound_cont"><sound.*?sound></span>', re.DOTALL), '', h3_cleaned)
            # nom déposé
            h3_cleaned = re.sub(re.compile('<span class="d_etm">\\(nom déposé\\)</span>', re.DOTALL), '', h3_cleaned)
            match = re.search(re.compile('^(.*?)<span class="d_cat">(.*)</span>', re.DOTALL), h3_cleaned)
            if match is not None:
                lem_matches = re.split('(?:, )|(?: <span class="d_mta">ou</span> )', match.group(1).strip())
                lexcat_matches = re.split('(?:, )|(?: <span class="d_x">et</span> )', match.group(2).strip())
                for lem_match in lem_matches:
                    for lexcat_match in lexcat_matches:
                        v = (lem_match, lexcat_match)
                        if v not in valids:
                            valids.append(v)
        for (lem_match, lexcat_match) in valids:
            if lem_match == lemma:
                if lexical_category != 'nom' and lexcat_match == lexical_category:
                    return True
                if lexical_category == 'numéral' and lexcat_match == 'adjectif numéral invariable':
                    return True
                if lexical_category == 'nom' and '{} {}'.format(lexical_category, gender) == lexcat_match:
                    return True
                if lexical_category == 'nom' and lexcat_match == 'nom' and (gender == 'féminin,masculin' or gender == 'masculin,féminin'):
                    return True
                if lexical_category == 'verbe' and lexcat_match in ('verbe intransitif', 'verbe pronominal', 'verbe transitif', 'verbe transitif indirect'):
                    return True
                if lexical_category == 'adverbe' and lexcat_match in ('adverbe', 'adverbe de temps'):
                    return True
        nouns = list(filter(lambda x: x[1] == 'nom', valids))
        if lexical_category == 'nom' and len(nouns) == 2 and nouns[0][1] == 'nom' and nouns[1][1] == 'nom' and (lemma == nouns[0][0] or lemma == nouns[1][0]):
            # print(lemma, lexical_category, gender, valids, nouns)
            return True
        # print(lemma, lexical_category, gender, valids)
        return False

    def get_id_from_redirect(self, r):
        redirect_id = json.loads(r['headers'])['location'][45:]
        if len(redirect_id) >= 1:
            return redirect_id
        return None

    def get_edit_summary(self):
        return '[[:d:Wikidata:Requests for permissions/Bot/EnvlhBot 2|Le Robert import]]'
