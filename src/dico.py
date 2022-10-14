import json
import time
import urllib.parse
import utils

from candidate import Candidate


class Dico:

    ADJECTIVE = 'Q34698'
    ADVERB = 'Q380057'
    CONJUNCTION = 'Q36484'
    INTERJECTION = 'Q83034'
    LOCUTION_ADVERBIAL = 'Q5978303'
    NOUN = 'Q1084'
    PERSONAL_PRONOUN = 'Q468801'
    PREPOSITION = 'Q4833830'
    VERB = 'Q24905'

    FEMININE = 'Q1775415'
    MASCULINE = 'Q499327'

    IGNORE = 'IGNORE'
    ACCEPT_ALL = 'ACCEPT_ALL'

    def __init__(self, db):
        self._db = db
        self.unknown_lexical_categories = dict()

    def fetch_lexemes_to_crawl(self):
        query = self.get_lexemes_to_crawl_query()
        url = 'https://query.wikidata.org/sparql?{}'.format(urllib.parse.urlencode({'query': query, 'format': 'json'}))
        return json.loads(utils.fetch_url(url).content)['results']['bindings']

    def crawl_url(self, url):
        print(url)
        r = utils.fetch_url(url)
        status_code = r.status_code
        headers = json.dumps(dict(r.headers), ensure_ascii=False)
        content = r.text
        self._db.save_crawl(url, status_code, headers, content)
        time.sleep(10)
        return {'status_code': status_code, 'headers': headers, 'content': content}

    def get_or_fetch_by_id(self, inferred_id):
        url = self.get_url().format(inferred_id)
        cache = self._db.get_url(url)
        if cache is not None:
            return cache
        return self.crawl_url(url)

    def process(self, lexeme):
        lemma = lexeme['lemma']['value']
        lexical_category = lexeme['lexicalCategory']['value'][31:]
        genders = set()
        if 'genders' in lexeme:
            for gender in lexeme['genders']['value'].split(','):
                if gender != '':
                    genders.add(gender[31:])
        inferred_id = self.infer_id(lemma)
        origin = Candidate(inferred_id, lemma, lexical_category, genders)
        success = False
        if len(inferred_id) >= 1:
            r = self.get_or_fetch_by_id(inferred_id)
            if r['status_code'] == 200:
                candidates = self.parse_content(r['content'], inferred_id)
                matches = self.match(origin, candidates)
                if len(matches) == 1:
                    success = True
                    inferred_id = matches.pop().parsed_id
                else:
                    print('origin     {}\ncandidates {}\nmatches    {}\n====='.format(origin, candidates, matches))
        return success, inferred_id

    def match(self, origin, candidates):
        matches = set()
        for candidate in candidates:
            if candidate.lexical_category == self.ACCEPT_ALL:
                matches.add(candidate)
            elif origin.lexical_category == self.NOUN:
                if origin.lemma == candidate.lemma and origin.lexical_category == candidate.lexical_category and origin.genders == candidate.genders:
                    matches.add(candidate)
            else:
                if origin.lemma == candidate.lemma and origin.lexical_category == candidate.lexical_category:
                    matches.add(candidate)
        return matches

    def get_property_id(self):
        raise NotImplementedError()

    def get_lexemes_to_crawl_query(self):
        raise NotImplementedError()

    def get_url(self):
        raise NotImplementedError()

    def infer_id(self, lemma):
        raise NotImplementedError()

    def parse_content(self, content, inferred_id):
        raise NotImplementedError()

    def get_id_from_redirect(self, r):
        raise NotImplementedError()

    def get_edit_summary(self):
        raise NotImplementedError()
