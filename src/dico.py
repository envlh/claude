import json
import time
import utils

from candidate import Candidate


class Dico:

    ABBREVIATION = 'Q102786'
    ADJECTIVE = 'Q34698'
    ADJECTIVE_DEMONSTRATIVE = 'Q2824480'
    ADJECTIVE_INDEFINITE = 'Q3618903'
    ADVERB = 'Q380057'
    ARTICLE = 'Q103184'
    CHEMICAL_SYMBOL = 'Q102500'
    CONJUNCTION = 'Q36484'
    CONJUNCTION_COORDINATING = 'Q28833099'
    INTERJECTION = 'Q83034'
    LOCUTION = 'Q3257782'
    LOCUTION_ADJECTIVAL = 'Q12734432'
    LOCUTION_ADVERBIAL = 'Q5978303'
    LOCUTION_CONJUNCTIVE = 'Q5978305'
    LOCUTION_NOMINAL = 'Q29888377'
    LOCUTION_VERBAL = 'Q10976085'
    NOUN = 'Q1084'
    NUMERAL = 'Q63116'
    PRONOUN_DEMONSTRATIVE = 'Q34793275'
    PRONOUN_INDEFINITE = 'Q956030'
    PRONOUN_INTERROGATIVE = 'Q54310231'
    PRONOUN_PERSONAL = 'Q468801'
    PRONOUN_RELATIVE = 'Q1050744'
    PREFIX = 'Q134830'
    PREPOSITION = 'Q4833830'
    SIGLE = 'Q918270'
    SUFFIX = 'Q102047'
    VERB = 'Q24905'

    FEMININE = 'Q1775415'
    MASCULINE = 'Q499327'

    IGNORE = 'IGNORE'
    ACCEPT_ALL = 'ACCEPT_ALL'

    def __init__(self, db, offline=False):
        self._db = db
        self._offline = offline
        self._last_query = 0
        self.unknown_lexical_categories = dict()

    def fetch_lexemes_to_crawl(self):
        return utils.sparql_query(self.get_lexemes_to_crawl_query())

    def crawl_url(self, url):
        if self._offline:
            status_code = 418
            headers = {}
            content = ''
        else:
            print(url)
            # sleeping 10 secondes between each query on the same dictionary
            diff = int(time.time()) - self._last_query
            if diff < 10:
                time.sleep(10 - diff)
            self._last_query = int(time.time())
            # crawl
            r = utils.fetch_url(url)
            status_code = r.status_code
            headers = json.dumps(dict(r.headers), ensure_ascii=False)
            content = r.text
            self._db.save_crawl(url, status_code, headers, content)
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
            if r['status_code'] in (301, 302):
                inferred_id = self.get_id_from_redirect(r)
                if inferred_id is not None:
                    r = self.get_or_fetch_by_id(inferred_id)
            if r['status_code'] == 200:
                candidates = self.parse_content(r['content'], inferred_id)
                matches = self.match(origin, candidates)
                if len(matches) == 1:
                    success = True
                    inferred_id = matches.pop().parsed_id
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

    def add_unknown_lexical_category(self, lexical_category):
        if lexical_category in self.unknown_lexical_categories:
            self.unknown_lexical_categories[lexical_category] += 1
        else:
            self.unknown_lexical_categories[lexical_category] = 1

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
